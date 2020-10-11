FROM alpine:3.10

RUN mkdir -p /samba/share && \
    chmod -R 0777 /samba/share && \
    chown -R nobody:nobody /samba/share

# install samba
RUN apk update && \
    apk add samba

# sambaの設定ファイル生成（めんどくさいので雑にGuestに全許可(Firewall等でホストを制限するなどが前提)）
RUN { \
    echo "[global]"; \
    echo "  security = user"; \
    echo "  map to guest = Bad User"; \
    echo "  guest account = nobody"; \
    echo "  min protocol = SMB2"; \
    echo "[public]"; \
    echo "  path = /samba/share"; \
    echo "  writable = no"; \
    echo "  guest ok = yes"; \
    echo "  guest only = yes"; \
    echo "  create mode = 0666"; \
    echo "  directory mode = 0777"; \
    } > /etc/samba/smb.conf
EXPOSE 139 445

# start smbd as foreground
ENTRYPOINT ["/bin/ash"]
CMD ["-c", "nmbd restart -D && smbd restart -FS --no-process-group </dev/null"]
