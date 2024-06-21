# Use the official Node.js image as a parent image
FROM node:18

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install


# Copy the rest of the application code to the working directory
COPY . .


# Expose the port that the app runs on
EXPOSE 8080

# Command to run the app
CMD ["node", "index.js"]
