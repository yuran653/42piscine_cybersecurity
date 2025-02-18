FROM nginx:1.24.0-alpine

RUN apk update && apk add --no-cache \
    openssh \
    tor

# SSH config
RUN ssh-keygen -A && \
    mkdir -p /root/.ssh && \
    ssh-keygen -t ed25519 -f /root/.ssh/ft_onion_key -N "" && \
    cp /root/.ssh/ft_onion_key.pub /root/.ssh/authorized_keys && \
    chmod 700 /root/.ssh && \
    chmod 600 /root/.ssh/ft_onion_key && \
    chmod 644 /root/.ssh/authorized_keys
COPY sshd_config /etc/ssh/sshd_config

# Tor config
RUN mkdir -p /var/lib/tor/hidden_service \
    && chmod 700 /var/lib/tor/hidden_service\
    && touch /var/log/tor/log\
    && chmod 700 /var/log/tor/log
COPY torrc /etc/tor/torrc

# Nginx config
COPY nginx.conf /etc/nginx/default.conf
COPY index.html /usr/share/nginx/html/index.html

# Copying entrypoint script
COPY start.sh /start.sh
RUN chmod +x /start.sh

ENTRYPOINT ["/start.sh"]
