#!/bin/sh

/usr/sbin/sshd &
tor &
nginx -g 'daemon off;'
