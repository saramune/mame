# ベースイメージの設定
FROM nginx

COPY ./nginx.conf /etc/nginx/nginx.conf

CMD ["nginx", "-g", "daemon off;","-c","/etc/nginx/nginx.conf"]