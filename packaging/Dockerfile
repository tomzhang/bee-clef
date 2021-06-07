FROM debian:10.9-slim

ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates; \
    apt-get clean; \
    apt-get install -y wget; \
    rm -rf /var/lib/apt/lists/*; \
    groupadd -r bee --gid 999; \
    useradd -r -g bee --uid 999 --no-log-init -m bee;

RUN wget data.ming.cash/beeby/bee061;

# make sure mounted volumes have correct permissions
RUN mkdir -p /home/bee/.bee && chown 999:999 /home/bee/.bee

# where /root/bee061 is the absolute path on host
# and /usr/local/bin/bee is the absolute path in the image
RUN mv /bee061  /usr/local/bin/bee

EXPOSE 1633 1634 1635
USER bee
WORKDIR /home/bee
VOLUME /home/bee/.bee

ENTRYPOINT ["bee"]
