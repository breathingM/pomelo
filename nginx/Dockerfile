#fpm + durian installing
FROM centos:centos7

MAINTAINER Michael


# edit yum mirrorlist nearby Taiwan
RUN sed -i 's/\(^mirrorlist.*\)$/\1\&cc=tw/g' /etc/yum.repos.d/CentOS-Base.repo

RUN yum update -y && yum clean all && \
    yum install -y epel-release && \
    yum install -y supervisor acl wget tar autoconf git nginx


# libicu
RUN wget http://download.icu-project.org/files/icu4c/52.1/icu4c-52_1-RHEL6-x64.tgz
RUN tar -C / -zxf icu4c-52_1-RHEL6-x64.tgz

RUN yum install -y libxml2-devel && \
    yum install -y openssl-devel && \
    yum install -y curl-devel libuuid-devel.x86_64 && \
    yum install -y glibc-headers gcc-c++ && \
    yum install -y libmcrypt libmcrypt-devel make

RUN echo '# max user processes' > /etc/security/limits.d/local.conf && \
    echo '*          soft    nproc     65535' >> /etc/security/limits.d/local.conf && \
    echo '*          hard    nproc     65535' >> /etc/security/limits.d/local.conf && \
    printf "\n"  >> /etc/security/limits.d/local.conf && \
    echo '# open files' >> /etc/security/limits.d/local.conf && \
    echo '*          soft    nofile    65535' >> /etc/security/limits.d/local.conf && \
    echo '*          hard    nofile    65535' >> /etc/security/limits.d/local.conf

RUN mkdir -p /var/www

WORKDIR /home/durian

# supervisord.conf
RUN sed -i -e '41,126d' /etc/supervisord.conf && \
    sed -i -e '33,35d' /etc/supervisord.conf && \
    sed -i -e '24,31d' /etc/supervisord.conf && \
    sed -i -e '5,13d' /etc/supervisord.conf && \
    sed -i 's/nodaemon=false/nodaemon=true/g' /etc/supervisord.conf && \
    printf '\n[program:nginx]\n' >> /etc/supervisord.conf && \
    printf 'command=/usr/sbin/nginx -c /etc/nginx/nginx.conf\n' >> /etc/supervisord.conf && \
    printf '\n[program:sysctl]\n' >> /etc/supervisord.conf && \
    printf 'command=sysctl -p' >> /etc/supervisord.conf && \
    printf '\nstartsecs=0\n' >> /etc/supervisord.conf && \
    printf 'autorestart=false\n' >> /etc/supervisord.conf && \
    printf '\n[program:setfacl]\n' >> /etc/supervisord.conf && \
    echo 'command=setfacl -R -m u:"nobody":rwX /var/www/app/cache /var/www/app/logs && \' >> /etc/supervisord.conf && \
    echo '        setfacl -dR -m u:"nobody":rwX /var/www/app/cache /var/www/app/logs' >> /etc/supervisord.conf && \
    printf '\nstartsecs=0\n' >> /etc/supervisord.conf && \
    printf 'autorestart=false' >> /etc/supervisord.conf

COPY nginx.conf /etc/nginx/nginx.conf
COPY bb.conf /etc/nginx/conf.d/
COPY sk.conf /etc/nginx/conf.d/
COPY default.conf /etc/nginx/conf.d/

RUN echo 'net.core.netdev_max_backlog=10000' >> /etc/sysctl.conf && \
    echo 'net.ipv4.tcp_max_syn_backlog=65535' >> /etc/sysctl.conf && \
    echo 'net.core.somaxconn=65535' >> /etc/sysctl.conf && \
    echo 'vm.swappiness=0' >> /etc/sysctl.conf

# tell Nginx to stay foregrounded
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

# expose HTTP
EXPOSE 80

CMD ["/usr/bin/supervisord"]
