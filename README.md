# Cat Identification Project
Proposal for the development of a cat type (limited breed, color, pattern etc) identification project using a deep convolutional neural network

A program or website which uses a deep convolutional neural network (DCNN) to identify the breed, color, and color pattern of a cat can increase the likelihood that an animal recovered by an animal shelter is successfully returned to its owner. Dogs and cats are lost with equal freqency, but cats are both less likely to be recovered at all, and much less likely to be recovered from animal shelters (http://www.mdpi.com/2076-2615/2/2/301, Fig 1). While some of this can be explained by other factors, proper, consistent identification of cat breeds and coat patters will help owners correctly identify the missing pet, and shelters correctly process an inquiry.

<p>
  <img src="/images/strays_rto.png" width="480" height="360" title="Fig 1">
  
  <em>Fig 1. The proportion of stray dogs which are returned to owners is much higher than the proportion of stray cats despite the fact that they are lost with equal frequency. (src: https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Outcomes/9t4d-g238 and https://data.austintexas.gov/Health-and-Community-Services/Austin-Animal-Center-Intakes/wter-evkm)</em>
</p>

I propose to train a DCNN via supervised learning to identify a set of the most common cat breeds, colors, and coat patterns. The kernel will then be usable to label an arbitrary cat image for public users to identify their animals, and for shelter workers to catalogue incoming strays. Since the output for a given cat will be the same for different images, making a match will be much easier.

Cat images are abundant on the internet. The main source comes from web scraping of the website PetFinder.com. In order to help keep the final product generalizable, I recover the url to the source images posted for each cat and download them. The entire process is fully automated. This has produced ~23,000 images of stray cats from shelters across the USA. I will combine this with two other public datasets of cat images: 12,000 images from the kaggle dogs-vs-cas challenge (www.kaggle.com/c/dogs-vs-cats/data), and a dataset of 10,000 images used to identify cat faces (https://archive.org/details/CAT_DATASET). 

While it might seem wise to scrape the breed and color information available on PetFinder.com, a significant fraction of that information is incorrect, especially for exotic animals. For that reason, the images will need to be labeled by one or more experts who agree. In support of this, I have already prepared an application for rapid labeling of the 45,000 images and identified an expert willing to perform the task. An image can be labeled in about 2 seconds, meaning an individual can label all of the images in approximately 25 hours.

I will develop the DCNN in python using keras with tensorflow as a backend. As a preliminary step, it is important to identify whether there is enough information in the images to classify them. In order to demonstrate this, I have used an unsupervised clustering model (src: https://github.com/elcorto/imagecluster) to identify sets of similar images. Many of the clusters produced are precisely drawn around the classes I wish to describe (see Fig 2).

<p>
  <img src="/images/cat_clusters.png" width="566" height="616" title="Fig 2">
  
  <em>Fig 2. Most of the images placed in one of the larger clusters show remarkable similarity. Supervised learning will preven the occasional misclassification (like the grey tabby in the top-right)</em>
</p>

With the DCNN kernel in hand, I will produce a resource that users and shelters can use to classify new images. This may be a website or a mobile application. Public users will be able to classify an image of a lost pet or take pictures of a stray to compare its classification with that of a missing animal. Further applications will include its use in scientific work such as the assessment of risk factors linked to genetics which express as breed or coat pattern (https://www.ncbi.nlm.nih.gov/pubmed/28612380)
