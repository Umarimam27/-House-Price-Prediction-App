# -House-Price-Prediction-App
This project delivers a complete end-to-end machine learning solution, from model training (using Linear Regression) to a highly interactive and visually stunning web application built with Streamlit.  Users can input key property features to receive real-time price predictions, all presented on a dynamic, high-visibility background.
✨ Key Features

Real-Time Prediction: Utilizes a Linear Regression model to predict house prices based on features like sqft_living, bedrooms, bathrooms, grade, and waterfront.

Interactive Web App (Streamlit): A modern, responsive user interface built using the Streamlit framework.

Aesthetic & Seamless Design: Features custom CSS to create a frosted glass/blur effect on content containers for high readability over a dynamic background.

Zero-Network Slideshow: Implements a unique Base64-encoded image slideshow feature, allowing users to upload and display a changing background of images without relying on an external network connection.

Full ML Pipeline: Includes a dedicated Jupyter Notebook (HousePricePrediction.ipynb) detailing the data cleaning, feature engineering, training, and model persistence process.

🛠️ Project Structure
The repository is organized into two main parts:

Model Training (HousePricePrediction.ipynb):

Data loading and initial exploration.

Feature selection and processing (e.g., handling categorical variables, scaling).

Training the final sklearn.linear_model.LinearRegression model.

Saving the model to disk as lr_model.pkl for deployment.

Web Application (HousePricePrediction.py):

Loads the pre-trained lr_model.pkl.

Implements the Streamlit layout with prediction inputs and model performance metrics.

Contains the advanced set_cinematic_bg function to handle the Base64 image upload and CSS slideshow logic.
<img width="1919" height="868" alt="image" src="https://github.com/user-attachments/assets/62417bf8-99e2-4cad-8288-f5efab5c2041" />


https://github.com/user-attachments/assets/17f62ed5-d973-46d5-b871-81c0cbd0971d




