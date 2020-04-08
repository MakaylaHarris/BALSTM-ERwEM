import pickle
import model
import multi_training
from main import gen_adaptive

if __name__ == '__main__':

    m = model.Model([300, 300], [100, 50], dropout=0.5)
    pcs = multi_training.loadPieces("music")
    # multi_training.trainPiece(m, pcs, 10000)
    # gen_adaptive(m, pcs, 10, name="composition")
    # pickle.dump(m.learned_config, open("path_to_weight_file.p", "wb"))
    data = pickle.load(open("output/params1500.p", "rb"))
    m.learned_config = data
    gen_adaptive(m, pcs, 10, name="composition")
