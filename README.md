retina.bovw.plosone
===================

retina.bovw.plosone is a complete, easy-to-use, and effective code for Diabetic Retinopathy (DR) detection and assessment of need for referral. It encompass the detecion of some of the most common DR-related lesions and a two-tiered image classification in order to evaluate the need for referral in the interval of 12 months. The lesions detected by the code are:
- Hard Exudates
- Superficial Hemorrhages
- Deep Hemorrhages
- Red Lesions (involve deep hemorrhages and superficial hemorrhages)
- Cotton-wool Spots
- Drusen

The methodology employed in the code, based upon bag of visual words (BoVW), employs a different strategy, associating a two-tiered image representation to maximum-margin support-vector machine (SVM) classifiers. Such methodology was widely explored for general-purpose image classification, and consists of the following steps:
(i) extraction of low-level local features from the image;
(ii) learning of a codebook using a training set of images;
(iii) creation of the mid-level (BoVW) representations for the images based on that codebook;
(iv) learning of a classification model for one particular lesion using an annotated training set;
(v) using the BoVW representation and the learned classification model for deciding on whether or not a specific lesion is present in a retinal image.

For the extraction of low-level features, two techniques are explored:
(i) sparse extraction: based upon the detection of salient regions or points of interest;
(ii) dense extraction: sampled over dense grids of different scales.

For the extraction of mid-level features, three methods are used, one of them was proposed in the current work:
(i) Hard assignment: associates each descriptor fully and only to its closest code word in the codebook. The advantage of these schemes is the sparsity of the codes; the disadvantages are that they are subject to imprecision and noise when the descriptors fall in regions close to the limit between the code words in the feature space;
(ii) Soft assignment: there are several “soft” assignment schemes developed to deal with the deficiencies associated with the hard assignment treatment. The option employed here was code word uncertainty, which has not been explored as a DR-related lesion detector but is generally considered the most effective for other classification tasks;
(iii) Semi-soft assignment: soft assignment solves the boundary effects of hard assignment, but creates codes, which are too dense. A “semi-soft” scheme is often more desirable. One such scheme was designed specially for the DR-related lesion detection.

The referral vs. non-referral classification is performed by the fusion of the individual DR-related lesions detectors. The most advanced way to perform the fusion is using a meta-classification approach. This referral-decider operates on high-level features obtained from a vector of scores consisting of the individual lesion detectors. The referral-decider is then trained using independent annotations.

retina.bovw.plosone is available at
[https://github.com/piresramon/retina.bovw.plosone](https://github.com/piresramon/retina.bovw.plosone)
Please read the [LICENSE](LICENSE) file before using retina.bovw.plosone.

Table of Contents
=================

- Quick Start
- Configuration and Data Organization
- 'low_level_script.py' Usage
- 'create_codebooks.py' Usage
- 'mid_level_script.py' Usage
- 'classification.py' Usage
- 'classify_image.py' Usage
- 'referral.py' Usage
- Tips on Practical Use
- Examples
- Library Usage
- Additional Information

Quick Start
===========

If you are new to retina.bovw.plosone and if the data is not large, please use general-script.py after configuration and data organization. It does everything automatic -- from low-level feature extraction, codebook creation, mid-level feature extraction, and DR-related detectors learning.

Usage: general-script.py

This will develop the models for every pair low-level/mi-level feature extraction and every DR-related lesions. After this, you can run the referral assessment code. For information, see "'referral.py' Usage".

Configuration and Data Organization
============================

The code was developed to run preferentially with DR1 and DR2 dataset, employing the cross-dataset validation protocol (training on DR1 and testing on DR2).
The datasets are available at http://dx.doi.org/10.6084/m9.figshare.953671
Before run the code, it's necessary to download the datasets and organize some directories:
(i) Uncompress DR1-images-by-lesions.zip  at source/datasets/DR1-images-by-lesions/ directory;
(ii) Uncompress DR2-images-by-lesions.zip  at source/datasets/DR2-images-by-lesions/ directory;
(ii) Uncompress DR1-images-by-lesions.zip at source/datasets/DR1-images-by-lesions/ directory;
(iv) Uncompress DR1-additional-marked-images.zip at source/datasets/DR1-additional-marked-images/ directory;
(v) Uncompress markings.zip at source/markings/ directory.

'low_level_script.py' Usage
============================
```
Usage: low_level_script.py [options]
options:
-h : show options
-train dataset : define the training dataset (default DR1)
	DR1 -- DR1 as the training dataset
	DR2 -- DR2 as the training dataset
-test dataset : define test dataset (default DR2)
	DR1 -- DR1 as the test dataset
	DR2 -- DR2 as the test dataset
-l lesion : define a specific DR-related lesion (default [exsudato-duro, hemorragia-superficial, hemorragia-profunda, lesoes-vermelhas, mancha-algodonosa, drusas-maculares, imagem-normal])
	exsudato-duro		 -- Hard Exudates
	hemorragia-superficial	 -- Superficial Hemorrhages
	hemorragia-profunda	 -- Deep Hemorrhages
	lesoes-vermelhas	 -- Red Lesions
	mancha-algodonosa	 -- Cotton-wool Spots
	drusas-maculares	 -- Drusen
	imagem-normal		 -- Normal Images
-low technique : define a specific low-level technique (default [sparse, dense])
	sparse -- Sparse low-level feature extraction
	dense  -- Dense low-level feature extraction
-t1 threshold : define the threshold for trainig dataset (default 3500)
-t2 threshold : define the threshold for test dataset (default 3500)
-surf path : define the path to the surf algorithm (default ./ext/surf/surf.ln)
```

'create_codebooks.py' Usage
============================
```
Usage: create_codebooks.py [options]
options:
-h : show options
-train dataset : define the training dataset (default DR1)
	DR1 -- DR1 as the training dataset
	DR2 -- DR2 as the training dataset
-l lesion : define a specific DR-related lesion (default [exsudato-duro, hemorragia-superficial, hemorragia-profunda, lesoes-vermelhas, mancha-algodonosa, drusas-maculares, imagem-normal])
	exsudato-duro		 -- Hard Exudates
	hemorragia-superficial	 -- Superficial Hemorrhages
	hemorragia-profunda	 -- Deep Hemorrhages
	lesoes-vermelhas	 -- Red Lesions
	mancha-algodonosa	 -- Cotton-wool Spots
	drusas-maculares	 -- Drusen
	imagem-normal		 -- Normal Images
-low technique : define a specific low-level technique (default [sparse, dense])
	sparse -- Sparse low-level feature extraction
	dense  -- Dense low-level feature extraction
-size s : length of the codebook (default 250 for sparse (resulting in a codebook of 500 codewords) and 125 for dense (resulting in a codebook of 1500 codewords))
-kmeans path : define the path to the k-means algorithm (default ./ext/kmeans/kmltest)
```

'mid_level_script.py' Usage
============================
```
Usage: mid_level_script.py [options]
options:
-h : show options
-train dataset : define the training dataset (default DR1)
	DR1 -- DR1 as the training dataset
	DR2 -- DR2 as the training dataset
-test dataset : define test dataset (default DR2)
	DR1 -- DR1 as the test dataset
	DR2 -- DR2 as the test dataset
-l lesion : define a specific DR-related lesion (default [exsudato-duro, hemorragia-superficial, hemorragia-profunda, lesoes-vermelhas, mancha-algodonosa, drusas-maculares, imagem-normal])
	exsudato-duro		 -- Hard Exudates
	hemorragia-superficial	 -- Superficial Hemorrhages
	hemorragia-profunda	 -- Deep Hemorrhages
	lesoes-vermelhas	 -- Red Lesions
	mancha-algodonosa	 -- Cotton-wool Spots
	drusas-maculares	 -- Drusen
-low technique : define a specific low-level technique (default [sparse, dense])
	sparse -- Sparse low-level feature extraction
	dense  -- Dense low-level feature extraction
-mid technique : define a specific mid-level technique (default [hard, semi, soft])
	hard -- Hard-Sum coding/pooling
	semi -- Semi-Soft-Sum coding/pooling
	soft -- Soft-Max coding/pooling
-i image : define the image name (used only for cases where we are interested in describing only one image)
```

'classification.py' Usage
============================
```
Usage: classification.py [options]
options:
-h : show options
-train dataset : define the training dataset (default DR1)
	DR1 -- DR1 as the training dataset
	DR2 -- DR2 as the training dataset
-test dataset : define test dataset (default DR2)
	DR1 -- DR1 as the test dataset
	DR2 -- DR2 as the test dataset
-l lesion : define a specific DR-related lesion (default [exsudato-duro, hemorragia-superficial, hemorragia-profunda, lesoes-vermelhas, mancha-algodonosa, drusas-maculares, imagem-normal])
	exsudato-duro		 -- Hard Exudates
	hemorragia-superficial	 -- Superficial Hemorrhages
	hemorragia-profunda	 -- Deep Hemorrhages
	lesoes-vermelhas	 -- Red Lesions
	mancha-algodonosa	 -- Cotton-wool Spots
	drusas-maculares	 -- Drusen
-low technique : define a specific low-level technique (default [sparse, dense])
	sparse -- Sparse low-level feature extraction
	dense  -- Dense low-level feature extraction
-mid technique : define a specific mid-level technique (default [hard, semi, soft])
	hard -- Hard-Sum coding/pooling
	semi -- Semi-Soft-Sum coding/pooling
	soft -- Soft-Max coding/pooling
-svm path : define the path to the svm algorithm (default ./ext/svm/)
-plot : use this parameter to plot the ROC curves (default False)
```

'classify_image.py' Usage
============================
```
Usage: classify_image.py [options]
options:
-h : show options
-i image : define the name of the image (from DR2 dataset, e.g.: IM000243.pgm)
-l lesion : define a specific DR-related lesion (default [exsudato-duro, hemorragia-superficial, hemorragia-profunda, lesoes-vermelhas, mancha-algodonosa, drusas-maculares, imagem-normal])
	exsudato-duro		 -- Hard Exudates
	hemorragia-superficial	 -- Superficial Hemorrhages
	hemorragia-profunda	 -- Deep Hemorrhages
	lesoes-vermelhas	 -- Red Lesions
	mancha-algodonosa	 -- Cotton-wool Spots
	drusas-maculares	 -- Drusen
-low technique : define a specific low-level technique (default [sparse, dense])
	sparse -- Sparse low-level feature extraction
	dense  -- Dense low-level feature extraction
-mid technique : define a specific mid-level technique (default [hard, semi, soft])
	hard -- Hard-Sum coding/pooling
	semi -- Semi-Soft-Sum coding/pooling
	soft -- Soft-Max coding/pooling
-o offset : define a specific offset of the hyperplane (use only when select a specific DR-related lesion)
-svm path : define the path to the svm algorithm (default ./ext/svm/)
```

'referral.py' Usage
============================
```
Usage: referral.py [options]
options:
-h : show options
-low technique : define a specific low-level technique (default [sparse, dense])
	sparse -- Sparse low-level feature extraction
	dense  -- Dense low-level feature extraction
-mid technique : define a specific mid-level technique (default [hard, semi, soft])
	hard -- Hard-Sum coding/pooling
	semi -- Semi-Soft-Sum coding/pooling
	soft -- Soft-Max coding/pooling
-svm path : define the path to the svm algorithm (default ./ext/svm/)
-plot : use this parameter to plot the ROC curves (default False)
```

Tips on Practical Use
============================

* Run low_level_script.py, create_codebook, and mid_level_script.py in several instances, each one especifying a lesion, a low-level technique and a mid-level technique. This can be done when are available several processors. Next versions of the code will explore multiprocessing advantages.
* If you will use other dataset for training, it will be required marking for the new images in the same format.

Examples
============================

> python low_level_script.py -l exsudato-duro -low sparse
> python low_level_script.py -l imagem-normal -low sparse
> python create_codebooks.py -l exsudato-duro -low sparse
> python create_codebooks.py -l imagem-normal -low sparse
> python mid_level_script.py -l exsudato-duro -low sparse
> python mid_level_script.py -l imagem-normal -low sparse
> python classification.py -l exsudato-duro -low sparse -plot

Describe sparsely the images with hard exudates and the normal images with SURF algorithm. After this, create three codebooks (one for each mid-level technique), describe the same images with the three codebooks, and finish with the classification. This results in a graphic (in pdf) with three ROC curves in 'classification/' directory.

> python low_level_script.py -l mancha-algodonosa -low dense -mid soft
> python low_level_script.py -l mancha-algodonosa -low dense -mid soft
> python create_codebooks.py -l mancha-algodonosa -low dense -mid soft
> python create_codebooks.py -l mancha-algodonosa -low dense -mid soft
> python mid_level_script.py -l mancha-algodonosa -low dense -mid soft
> python mid_level_script.py -l mancha-algodonosa -low dense -mid soft
> python classification.py -l mancha-algodonosa -low dense -mid soft -plot

Describe densely the images with cotton-wool spot and the normal images with SURF algorithm. After this, create the codebooks for soft assignment, describe the same images with the soft-max coding/pooling technique, and finish with the classification. This results in a graphic (in pdf) with one ROC curves in 'classification/' directory.

> python low_level_script.py
> python create_codebooks.py
> python mid_level_script.py
> python classification.py

Describe sparsely and densely all the images (including the images labeled as referable ou not referable, the images with marked regions, etc.) with SURF algorithm. After this, create codebooks for every combination low-level/mid-level, describe the images with each codebook, and finish with the classification. This results in six graphics, one per lesion, (in pdf) with six ROC curves in 'classification/' directory.

> python classify_image.py -i IM000243.pgm -l lesoes-vermelhas

Classify the image IM000243.pgm with the Red Lesions model. Return a score and the label (sick or normal).

> python classify_image.py -i IM000243.pgm

Classify the image IM000243.pgm with the six models. Return six scores and the labels (sick or normal), one for each DR-related lesion.

> python referral.py -low sparse -plot

Classify the images labeled as referable or non-referable with 18 model (6 lesions * 1 low-level technique * 3 mid-levels techniques). Three feature vector will be created, one for each pair low-level/mid-level technique, containing the scores obtained for each DR-related lesion. Three classifiers will be created. This results in a graphic (in pdf) with three ROC curves in 'referral/' directory.

Required Libraries
============================

- python.numpy
- python.scipy
- python.matplotlib

Additional Information
======================

If you find retina.bovw.plosone helpful, please cite it as

Pires, Ramon; F. Jelinek, Herbert; Wainer, Jacques; Valle, Eduardo; Rocha, Anderson (In Press): Advancing Bag-of-Visual-Words Representations for Lesion Classification in Retinal Images. PLOS ONE.

retina.bovw.plosone implementation document is available at
[http://www.recod.ic.unicamp.br/~piresramon](http://www.recod.ic.unicamp.br/~piresramon)

For any questions and comments, please email <mailto:pires.ramon@ic.unicamp.br>

Acknowledgments:
This work was supported in part by São Paulo Research Foundation FAPESP (http://www.fapesp.br) under Grant 2010/05647-4 and Grant 2011/15349-3, National Counsel of Technological and Scientific Development (CNPq) (http://www.cnpq.br) under Grant 307018/2010-5 and Grant 304352/2012-8, Microsoft Research (http://research.microsoft.com) and Samsung Eletrônica da Amazônia (http://www.samsung.com). The funders had no role in study design, data collection and analysis, decision to publish, or preparation of the manuscript.
