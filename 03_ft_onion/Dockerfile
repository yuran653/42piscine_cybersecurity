FROM nginx:1.24.0-alpine

RUN apk update && apk add --no-cache \
    openssh \
    tor

# SSH config
RUN ssh-keygen -A
COPY sshd_config /etc/ssh/sshd_config

# Tor config
RUN mkdir -p /var/lib/tor/hidden_service \
    # && chown -R tor:tor /var/lib/tor/hidden_service \
    && chmod 700 /var/lib/tor/hidden_service\
    && touch /var/log/tor/log
    # && chown tor:tor /var/log/tor/log\
    # && chmod 700 /var/log/tor/log
COPY torrc /etc/tor/torrc

# Nginx config
COPY nginx.conf /etc/nginx/default.conf
COPY index.html /usr/share/nginx/html/index.html

ENTRYPOINT ["sh", "-c", "tor & /usr/sbin/sshd -D & nginx -g 'daemon off;'"]
