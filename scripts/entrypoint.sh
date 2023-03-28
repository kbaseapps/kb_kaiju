#!/bin/bash

progenomes_VER=2021-03-02
nr_euk_VER=2022-03-10
nr_VER=2022-03-10
refseq_VER=2022-03-23
fungi_VER=2022-03-29
viruses_VER=2022-03-29
plasmids_VER=2022-04-10
rvdb_VER=2022-04-07


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

  echo "downloading: https://kaiju.binf.ku.dk/database/kaiju_db_refseq_$refseq_VER.tgz"
  mkdir -p /data/kaijudb/refseq
  cd /data/kaijudb/
  curl -o kaiju_db_refseq_$refseq_VER.tgz https://kaiju.binf.ku.dk/database/kaiju_db_refseq_$refseq_VER.tgz
  tar -xzf kaiju_db_refseq_$refseq_VER.tgz
  mv kaiju_db_refseq.fmi refseq/kaiju_db_refseq.fmi
  mv names.dmp refseq/names.dmp
  mv nodes.dmp refseq/nodes.dmp
  rm kaiju_db_refseq_$refseq_VER.tgz

  echo "downloading: https://kaiju.binf.ku.dk/database/kaiju_db_progenomes_$progenomes_VER.tgz"
  mkdir -p /data/kaijudb/progenomes
  cd /data/kaijudb/
  curl -o kaiju_db_progenomes_$progenomes_VER.tgz https://kaiju.binf.ku.dk/database/kaiju_db_progenomes_$progenomes_VER.tgz
  tar -xzf kaiju_db_progenomes_$progenomes_VER.tgz
  mv kaiju_db_progenomes.fmi progenomes/kaiju_db_progenomes.fmi
  mv names.dmp progenomes/names.dmp
  mv nodes.dmp progenomes/nodes.dmp
  rm kaiju_db_progenomes_$progenomes_VER.tgz

  echo "downloading: https://kaiju.binf.ku.dk/database/kaiju_db_nr_$nr_VER.tgz"
  mkdir -p /data/kaijudb/nr
  cd /data/kaijudb/
  curl -o kaiju_db_nr_$nr_VER.tgz https://kaiju.binf.ku.dk/database/kaiju_db_nr_$nr_VER.tgz
  tar -xzf kaiju_db_nr_$nr_VER.tgz
  mv kaiju_db_nr.fmi nr/kaiju_db_nr.fmi
  mv names.dmp nr/names.dmp
  mv nodes.dmp nr/nodes.dmp
  rm kaiju_db_nr_$nr_VER.tgz

  echo "downloading: https://kaiju.binf.ku.dk/database/kaiju_db_nr_euk_$nr_euk_VER.tgz"
  mkdir -p /data/kaijudb/nr_euk
  cd /data/kaijudb/
  curl -o kaiju_db_nr_euk_$nr_euk_VER.tgz https://kaiju.binf.ku.dk/database/kaiju_db_nr_euk_$nr_euk_VER.tgz
  tar -xzf kaiju_db_nr_euk_$nr_euk_VER.tgz
  mv kaiju_db_nr_euk.fmi nr_euk/kaiju_db_nr_euk.fmi
  mv names.dmp nr_euk/names.dmp
  mv nodes.dmp nr_euk/nodes.dmp
  rm kaiju_db_nr_euk_$nr_euk_VER.tgz

  echo "downloading: https://kaiju.binf.ku.dk/database/kaiju_db_viruses_$viruses_VER.tgz"
  mkdir -p /data/kaijudb/viruses
  cd /data/kaijudb/
  curl -o kaiju_db_viruses_$viruses_VER.tgz https://kaiju.binf.ku.dk/database/kaiju_db_viruses_$viruses_VER.tgz
  tar -xzf kaiju_db_viruses_$viruses_VER.tgz
  mv kaiju_db_viruses.fmi viruses/kaiju_db_viruses.fmi
  mv names.dmp viruses/names.dmp
  mv nodes.dmp viruses/nodes.dmp
  rm kaiju_db_viruses_$viruses_VER.tgz

  echo "downloading: https://kaiju.binf.ku.dk/database/kaiju_db_plasmids_$plasmids_VER.tgz"
  mkdir -p /data/kaijudb/plasmids
  cd /data/kaijudb/
  curl -o kaiju_db_plasmids_$plasmids_VER.tgz https://kaiju.binf.ku.dk/database/kaiju_db_plasmids_$plasmids_VER.tgz
  tar -xzf kaiju_db_plasmids_$plasmids_VER.tgz
  mv kaiju_db_plasmids.fmi plasmids/kaiju_db_plasmids.fmi
  mv names.dmp plasmids/names.dmp
  mv nodes.dmp plasmids/nodes.dmp
  rm kaiju_db_plasmids_$plasmids_VER.tgz

  echo "downloading: https://kaiju.binf.ku.dk/database/kaiju_db_rvdb_$rvdb_VER.tgz"
  mkdir -p /data/kaijudb/rvdb
  cd /data/kaijudb/
  curl -o kaiju_db_rvdb_$rvdb_VER.tgz https://kaiju.binf.ku.dk/database/kaiju_db_rvdb_$rvdb_VER.tgz
  tar -xzf kaiju_db_rvdb_$rvdb_VER.tgz
  mv kaiju_db_rvdb.fmi rvdb/kaiju_db_rvdb.fmi
  mv names.dmp rvdb/names.dmp
  mv nodes.dmp rvdb/nodes.dmp
  rm kaiju_db_rvdb_$rvdb_VER.tgz

  echo "downloading: https://kaiju.binf.ku.dk/database/kaiju_db_fungi_$fungi_VER.tgz"
  mkdir -p /data/kaijudb/fungi
  cd /data/kaijudb/
  curl -o kaiju_db_fungi_$fungi_VER.tgz https://kaiju.binf.ku.dk/database/kaiju_db_fungi_$fungi_VER.tgz
  tar -xzf kaiju_db_fungi_$fungi_VER.tgz
  mv kaiju_db_fungi.fmi fungi/kaiju_db_fungi.fmi
  mv names.dmp fungi/names.dmp
  mv nodes.dmp fungi/nodes.dmp
  rm kaiju_db_fungi_$fungi_VER.tgz

  cd /data/kaijudb

  if [ -s "/data/kaijudb/refseq/kaiju_db_refseq.fmi" -a -s "/data/kaijudb/progenomes/kaiju_db_progenomes.fmi" -a -s "/data/kaijudb/nr/kaiju_db_nr.fmi" -a -s "/data/kaijudb/nr_euk/kaiju_db_nr_euk.fmi" -a -s "/data/kaijudb/viruses/kaiju_db_viruses.fmi" -a -s "/data/kaijudb/plasmids/kaiju_db_plasmids.fmi" -a -s "/data/kaijudb/rvdb/kaiju_db_rvdb.fmi" -a -s "/data/kaijudb/fungi/kaiju_db_fungi.fmi" ] ; then
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
