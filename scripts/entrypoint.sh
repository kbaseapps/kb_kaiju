#!/bin/bash

. /kb/deployment/user-env.sh

python ./scripts/prepare_deploy_cfg.py ./deploy.cfg ./work/config.properties

if [ -f ./work/token ] ; then
  export KB_AUTH_TOKEN=$(<./work/token)
fi

if [ $# -eq 0 ] ; then
  sh ./scripts/start_server.sh
elif [ "${1}" = "test" ] ; then
  echo "Run Tests"
  make test
elif [ "${1}" = "async" ] ; then
  #sh ./scripts/run_async.sh
  xvfb-run bash ./scripts/run_async.sh
elif [ "${1}" = "init" ] ; then
  echo "Initialize module"
  mkdir -p /data/kaijudb
  cd /data/kaijudb

  echo "downloading: http://kaiju.binf.ku.dk/database/kaiju_db_refseq_2020-05-25.tgz"
  mkdir -p /data/kaijudb/refseq
  cd /data/kaijudb/
  wget -q http://kaiju.binf.ku.dk/database/kaiju_db_refseq_2020-05-25.tgz
  tar -xzf kaiju_db_refseq_2020-05-25.tgz
  mv kaiju_db_refseq.fmi refseq/kaiju_db_refseq.fmi
  mv names.dmp refseq/names.dmp
  mv nodes.dmp refseq/nodes.dmp
  rm kaiju_db_refseq_2020-05-25.tgz

  echo "downloading: http://kaiju.binf.ku.dk/database/kaiju_db_progenomes_2020-05-25.tgz"
  mkdir -p /data/kaijudb/progenomes
  cd /data/kaijudb/
  wget -q http://kaiju.binf.ku.dk/database/kaiju_db_progenomes_2020-05-25.tgz
  tar -xzf kaiju_db_progenomes_2020-05-25.tgz
  mv kaiju_db_progenomes.fmi progenomes/kaiju_db_progenomes.fmi
  mv names.dmp progenomes/names.dmp
  mv nodes.dmp progenomes/nodes.dmp
  rm kaiju_db_progenomes_2020-05-25.tgz

  echo "downloading: http://kaiju.binf.ku.dk/database/kaiju_db_nr_2020-05-25.tgz"
  mkdir -p /data/kaijudb/nr
  cd /data/kaijudb/
  wget -q http://kaiju.binf.ku.dk/database/kaiju_db_nr_2020-05-25.tgz
  tar -xzf kaiju_db_nr_2020-05-25.tgz
  mv kaiju_db_nr.fmi nr/kaiju_db_nr.fmi
  mv names.dmp nr/names.dmp
  mv nodes.dmp nr/nodes.dmp
  rm kaiju_db_nr_2020-05-25.tgz

  echo "downloading: http://kaiju.binf.ku.dk/database/kaiju_db_nr_euk_2020-05-25.tgz"
  mkdir -p /data/kaijudb/nr_euk
  cd /data/kaijudb/
  wget -q http://kaiju.binf.ku.dk/database/kaiju_db_nr_euk_2020-05-25.tgz
  tar -xzf kaiju_db_nr_euk_2020-05-25.tgz
  mv kaiju_db_nr_euk.fmi nr_euk/kaiju_db_nr_euk.fmi
  mv names.dmp nr_euk/names.dmp
  mv nodes.dmp nr_euk/nodes.dmp
  rm kaiju_db_nr_euk_2020-05-25.tgz

  cd /data/kaijudb

  if [ -s "/data/kaijudb/refseq/kaiju_db_refseq.fmi" -a -s "/data/kaijudb/progenomes/kaiju_db_progenomes.fmi" -a -s "/data/kaijudb/nr/kaiju_db_nr.fmi" -a -s "/data/kaijudb/nr_euk/kaiju_db_nr_euk.fmi" ] ; then
    echo "DATA DOWNLOADED SUCCESSFULLY"
    touch /data/__READY__
  else
    echo "Init failed"
  fi
elif [ "${1}" = "bash" ] ; then
  bash
elif [ "${1}" = "report" ] ; then
  export KB_SDK_COMPILE_REPORT_FILE=./work/compile_report.json
  make compile
else
  echo Unknown
fi
