import cv2 
import time 
import os 
import openface

imgDim = 96 
cuda = False

modelDir = '/home/pexea12/repos/openface/models'
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

networkModel = os.path.join(openfaceModelDir, 'nn4.small2.v1.t7')

net = openface.TorchNeuralNet(networkModel, imgDim=imgDim, cuda=cuda)


align = openface.AlignDlib(os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))

def getRep(imgPath, multiple=False, verbose=True):
    start = time.time()
    bgrImg = cv2.imread(imgPath)
    if bgrImg is None:
        raise Exception("Unable to load image: {}".format(imgPath))

    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)

    if verbose:
        print("  + Original size: {}".format(rgbImg.shape))
    if verbose:
        print("Loading the image took {} seconds.".format(time.time() - start))

    start = time.time()

    if multiple:
        bbs = align.getAllFaceBoundingBoxes(rgbImg)
    else:
        bb1 = align.getLargestFaceBoundingBox(rgbImg)
        bbs = [bb1]
    if len(bbs) == 0 or (not multiple and bb1 is None):
        raise Exception("Unable to find a face: {}".format(imgPath))
    if verbose:
        print("Face detection took {} seconds.".format(time.time() - start))

    reps = []
    for bb in bbs:
        start = time.time()
        alignedFace = align.align(
            imgDim,
            rgbImg,
            bb,
            landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
        if alignedFace is None:
            raise Exception("Unable to align image: {}".format(imgPath))
        if verbose:
            print("Alignment took {} seconds.".format(time.time() - start))
            print("This bbox is centered at {}, {}".format(bb.center().x, bb.center().y))

        start = time.time()
        rep = net.forward(alignedFace)
        if verbose:
            print("Neural network forward pass took {} seconds.".format(
                time.time() - start))
        reps.append((bb.center().x, rep))
    sreps = sorted(reps, key=lambda x: x[0])
    return sreps

print(getRep('jen.jpg'))