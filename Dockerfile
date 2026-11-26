# syntax=docker/dockerfile:1
FROM node:22-alpine AS build
WORKDIR /app
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml tsconfig*.json vite.config.ts index.html ./
COPY src ./src
COPY functions ./functions
COPY data/i18n ./data/i18n
ARG VITE_COMFYUI_BASE_URL=/comfy
ENV VITE_COMFYUI_BASE_URL=${VITE_COMFYUI_BASE_URL}
RUN corepack enable && pnpm install --frozen-lockfile && pnpm build

FROM nginx:1.29-alpine
# Only substitute COMFYUI_URL; preserve Nginx runtime variables such as $uri and $host.
ENV NGINX_ENVSUBST_VARS='${COMFYUI_URL}'
COPY docker/nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html
# Keep only the small UI translation bundle in the image; gallery data/images come from ComfyUI APIs.
COPY --from=build /app/data/i18n /usr/share/nginx/html/data/i18n
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=3s CMD wget -q -O /dev/null http://127.0.0.1/ || exit 1
