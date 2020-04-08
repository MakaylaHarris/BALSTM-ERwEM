import mido
import numpy

lowerBound = 24
upperBound = 102


def midiToNoteStateMatrix(midifile):
    # pattern = midi.read_midifile(midifile)
    pattern = mido.MidiFile(midifile)

    # timeleft = [track[0].tick for track in pattern]
    timeleft = []
    for track in pattern.tracks:
        timeleft.append(track[0].time)

    posns = [0 for track in pattern]

    statematrix = []
    span = upperBound - lowerBound
    time = 0

    state = [[0, 0] for x in range(span)]
    statematrix.append(state)
    while True:
        # if time % (pattern.resolution / 4) == (pattern.resolution / 8):
        if time % (pattern.ticks_per_beat / 4) == (pattern.ticks_per_beat / 8):
            # Crossed a note boundary. Create a new state, defaulting to holding notes
            oldstate = state
            state = [[oldstate[x][0], 0] for x in range(span)]
            statematrix.append(state)

        for i in range(len(timeleft)):
            while timeleft[i] == 0:
                track = pattern.tracks[i]
                pos = posns[i]

                evt = track[pos]
                # if isinstance(evt, midi.NoteEvent):
                if isinstance(evt, mido.Message):
                    if evt.type is 'note_on' or evt.type is 'note_off':
                        if (evt.note < lowerBound) or (evt.note >= upperBound):
                            pass
                            # print "Note {} at time {} out of bounds (ignoring)".format(evt.pitch, time)
                        else:
                            # if isinstance(evt, midi.NoteOffEvent) or evt.velocity == 0:
                            if evt.type is 'note_off' or evt.velocity == 0:
                                state[evt.note - lowerBound] = [0, 0]
                            else:
                                state[evt.note - lowerBound] = [1, 1]
                elif isinstance(evt, mido.MetaMessage) and evt.type is 'time_signature':
                    if evt.numerator not in (2, 4):
                        # We don't want to worry about non-4 time signatures. Bail early!
                        # print "Found time signature event {}. Bailing!".format(evt)
                        return statematrix

                try:
                    timeleft[i] = track[pos + 1].time
                    posns[i] += 1
                except IndexError:
                    timeleft[i] = None

            if timeleft[i] is not None:
                timeleft[i] -= 1

        if all(t is None for t in timeleft):
            break

        time += 1

    return statematrix


def noteStateMatrixToMidi(statematrix, name="example"):
    statematrix = numpy.asarray(statematrix)
    # pattern = midi.Pattern()
    pattern = mido.MidiFile()
    track = mido.MidiTrack()
    pattern.tracks.append(track)

    track.append(mido.Message('program_change', program=12))

    span = upperBound - lowerBound
    tickscale = 55

    lastcmdtime = 0
    prevstate = [[0, 0] for x in range(span)]
    for time, state in enumerate(statematrix + [prevstate[:]]):
        offNotes = []
        onNotes = []
        for i in range(span):
            n = state[i]
            p = prevstate[i]
            if p[0] == 1:
                if n[0] == 0:
                    offNotes.append(i)
                elif n[1] == 1:
                    offNotes.append(i)
                    onNotes.append(i)
            elif n[0] == 1:
                onNotes.append(i)
        for note in offNotes:
            track.append(mido.Message('note_off', time=(time - lastcmdtime) * tickscale, note=note + lowerBound))
            lastcmdtime = time
        for note in onNotes:
            track.append(
                mido.Message('note_on', time=(time - lastcmdtime) * tickscale, velocity=40, note=note + lowerBound))
            lastcmdtime = time

        prevstate = state

    # eot = midi.EndOfTrackEvent(tick=1)
    # track.append(eot)

    pattern.save(f"{name}.mid")
