# Stage 1: Build - Install dependencies
FROM node:18-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Stage 2: Production - Copy only what's needed
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY package.json ./
COPY server.js ./
COPY server.test.js ./

# Expose the port the app runs on
EXPOSE 8080

# Command to run the app
CMD ["npm", "start"]