




mkdir -p /tmp/uwsgi
mkdir -p /tmp/uwsgi/log

uwsgi --chdir=/data2/lipan/RNAProb \
    --module=RNAProb.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=RNAProb.settings \
    --master --pidfile=/data2/lipan/RNAProb/RNAProb-master.pid \
    --socket=0.0.0.0:12345 \
    --processes=5 \
    --harakiri=20 \
    --max-requests=5000 \
    --buffer-size 32768 \
    --vacuum \
    --protocol=http \
    --static-map /static=/data2/lipan/RNAProb/static \
    --daemonize=/data2/lipan/RNAProb/RNAProb.log






