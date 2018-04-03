FROM node:8.11
EXPOSE 8081
workdir /home/angular_frontend
COPY ./angular_frontend/package.json .
RUN npm install
COPY ./angular_frontend .
CMD ["node", "./index.js"]
