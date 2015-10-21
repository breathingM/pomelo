#fpm + durian installing
FROM centos:centos7

MAINTAINER Michael

# edit yum mirrorlist nearby Taiwan
RUN sed -i 's/\(^mirrorlist.*\)$/\1\&cc=tw/g' /etc/yum.repos.d/CentOS-Base.repo

RUN yum update -y && yum clean all && \
    yum install -y epel-release && \
    yum install -y supervisor acl wget tar autoconf git

# libicu
RUN wget http://download.icu-project.org/files/icu4c/52.1/icu4c-52_1-RHEL6-x64.tgz
RUN tar -C / -zxf icu4c-52_1-RHEL6-x64.tgz

RUN yum install -y libxml2-devel && \
    yum install -y openssl-devel && \
    yum install -y curl-devel libuuid-devel.x86_64 && \
    yum install -y glibc-headers gcc-c++ && \
    yum install -y libmcrypt libmcrypt-devel make

# php
RUN wget http://jp2.php.net/distributions/php-5.5.22.tar.gz
RUN tar -C . -zxf php-5.5.22.tar.gz
WORKDIR php-5.5.22
RUN ./configure --prefix=/usr/local/web/php \
                --with-libdir=lib64 \
                --enable-fpm --with-fpm-user=nobody --with-fpm-group=nobody \
                --with-config-file-path=/etc \
                --disable-ipv6 \
                --with-mcrypt=shared \
                --enable-mbstring \
                --with-openssl=shared \
                --with-libxml-dir=/usr/lib \
                --with-curl=shared \
                --enable-sockets \
                --with-zlib --with-iconv --with-gettext \
                --enable-intl --enable-bcmath=shared --enable-mysqlnd=shared --with-pdo-mysql=shared && \
    make && \
    make install

# php-fpm.conf
RUN cp /usr/local/web/php/etc/php-fpm.conf.default /usr/local/web/php/etc/php-fpm.conf
RUN sed -i 's/;pid\ =\ run\/php-fpm.pid/pid\ =\ \/var\/run\/php-fpm.pid/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/;error_log\ =\ log\/php-fpm.log/error_log\ =\ \/var\/log\/php-fpm\/php-fpm.log/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/listen\ =\ 127.0.0.1:9000/listen\ =\ \/var\/run\/durian\/php-fpm.sock/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/;listen.backlog\ =\ 65535/listen.backlog\ =\ 4096/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/;listen.mode\ =\ 0660/listen.mode\ =\ 0666/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/;pm.status_path\ =\ \/status/pm.status_path\ =\ \/status/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/pm.max_children.*/pm.max_children\ =\ 300/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/pm.start_servers.*/pm.start_servers\ =\ 87/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/pm.min_spare_servers.*/pm.min_spare_servers\ =\ 50/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/pm.max_spare_servers.*/pm.max_spare_servers\ =\ 225/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/;pm.max_requests.*/pm.max_requests\ =\ 50000/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/;slowlog.*/slowlog\ =\ \/var\/log\/php-fpm\/\$pool.log.slow/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/;ping.path\ =\ \/ping/ping.path\ =\ \/ping/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/;ping.response\ =\ pong/ping.response\ =\ ok/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/;request_terminate_timeout\ =\ 0/request_terminate_timeout\ =\ 60s/g' /usr/local/web/php/etc/php-fpm.conf && \
    sed -i 's/;daemonize\ =\ yes/daemonize\ =\ no/g' /usr/local/web/php/etc/php-fpm.conf    

# php.ini
RUN cp php.ini-development /etc/php.ini
RUN sed -i 's/expose_php\ =\ On/expose_php\ =\ Off/g' /etc/php.ini && \
    sed -i 's/error_reporting\ =\ E_ALL/error_reporting\ =\ E_ALL\ |\ E_STRICT/g' /etc/php.ini && \
    sed -i 's/display_errors\ =\ On/display_errors\ =\ Off/g' /etc/php.ini && \
    echo 'extension_dir = "/usr/local/web/php/lib/php/extensions/no-debug-non-zts-20121212/"' >> /etc/php.ini && \
    sed -i 's/;date.timezone\ =/date.timezone\ =\ "Asia\/Taipei"/g' /etc/php.ini && \
    sed -i 's/;opcache.enable=0/opcache.enable=1/g' /etc/php.ini && \
    sed -i 's/;opcache.memory_consumption=64/opcache.memory_consumption=128M/g' /etc/php.ini && \
    echo 'extension=bcmath.so' >> /etc/php.ini && \
    echo 'extension=curl.so' >> /etc/php.ini && \
    echo 'extension=mcrypt.so' >> /etc/php.ini && \
    echo 'extension=mysqlnd.so' >> /etc/php.ini && \
    echo 'extension=openssl.so' >> /etc/php.ini && \
    echo 'extension=uuid.so' >> /etc/php.ini && \
    echo 'extension=pdo_mysql.so' >> /etc/php.ini && \
    echo 'zend_extension=opcache.so' >> /etc/php.ini
RUN ln -s /usr/local/web/php/sbin/* /usr/local/sbin/
RUN ln -s /usr/local/web/php/bin/* /usr/local/bin/

# uuid
RUN wget https://pecl.php.net/get/uuid-1.0.3.tgz
RUN tar zxf uuid-1.0.3.tgz
WORKDIR uuid-1.0.3
RUN /usr/local/web/php/bin/phpize
RUN ./configure --with-libdir=lib64 --with-php-config=/usr/local/web/php/bin/php-config
RUN make && make install

RUN echo '# max user processes' > /etc/security/limits.d/local.conf && \
    echo '*          soft    nproc     65535' >> /etc/security/limits.d/local.conf && \
    echo '*          hard    nproc     65535' >> /etc/security/limits.d/local.conf && \
    printf "\n"  >> /etc/security/limits.d/local.conf && \
    echo '# open files' >> /etc/security/limits.d/local.conf && \
    echo '*          soft    nofile    65535' >> /etc/security/limits.d/local.conf && \
    echo '*          hard    nofile    65535' >> /etc/security/limits.d/local.conf

RUN mkdir -p /var/www
RUN mkdir -p /var/log/php-fpm
RUN curl -sS https://getcomposer.org/installer | php -- --install-dir=/bin

WORKDIR /home/durian

# supervisord.conf
RUN sed -i -e '41,126d' /etc/supervisord.conf && \
    sed -i -e '33,35d' /etc/supervisord.conf && \
    sed -i -e '24,31d' /etc/supervisord.conf && \
    sed -i -e '5,13d' /etc/supervisord.conf && \
    sed -i 's/nodaemon=false/nodaemon=true/g' /etc/supervisord.conf && \
    printf '\n[program:php-fpm]\n' >> /etc/supervisord.conf && \
    printf 'command=/usr/local/sbin/php-fpm\n' >> /etc/supervisord.conf && \
    printf '\n[program:sysctl]\n' >> /etc/supervisord.conf && \
    printf 'command=sysctl -p' >> /etc/supervisord.conf && \
    printf '\nstartsecs=0\n' >> /etc/supervisord.conf && \
    printf 'autorestart=false\n' >> /etc/supervisord.conf && \
    printf '\n[program:setfacl]\n' >> /etc/supervisord.conf && \
    echo 'command=setfacl -R -m u:"nobody":rwX /var/www/app/cache /var/www/app/logs && \' >> /etc/supervisord.conf && \
    echo '        setfacl -dR -m u:"nobody":rwX /var/www/app/cache /var/www/app/logs' >> /etc/supervisord.conf && \
    printf '\nstartsecs=0\n' >> /etc/supervisord.conf && \
    printf 'autorestart=false' >> /etc/supervisord.conf

COPY opcache_info.php /usr/local/web/

RUN echo 'net.core.netdev_max_backlog=10000' >> /etc/sysctl.conf && \
    echo 'net.ipv4.tcp_max_syn_backlog=65535' >> /etc/sysctl.conf && \
    echo 'net.core.somaxconn=65535' >> /etc/sysctl.conf && \
    echo 'vm.swappiness=0' >> /etc/sysctl.conf

EXPOSE 9000

CMD ["/usr/bin/supervisord"]
