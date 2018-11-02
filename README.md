# Introduction

This package connects the bfabric system to the python and R world providing a JSON and REST interface.
The [bfabricShiny](https://github.com/cpanse/bfabricShiny) R package is also a powerful extension interfacing the R world.

# bfabric wsdl python package

## Install 

- install current stable debian linux release

- install the python package as follow:

```{sh}
apt-get install python-pip

git clone git@github.com:cpanse/bfabricPy.git 
# svn co http://fgcz-svn/repos/scripts/trunk/linux/bfabric/apps/python bfabric-python bfabricPy

cd bfabricPy

python setup.py sdist

sudo pip install dist/bfabric*.gz -e .
```

## WSDL Interface to B-Fabric
[endpoints](http://fgcz-bfabric.uzh.ch/bfabric/workunit?wsdl)

## sample query
```sh
bfabric_list.py application
```

# See also

- [wsdl4BFabric](http://fgcz-intranet.uzh.ch/tiki-index.php?page=wsdl4BFabric)

# Most frequently used command lines

get useless stuff out of the system
```{sh} 
 bfabric_list_pending_workunits.py  \
   | grep cpanse \
   | grep 2015-09-0 \
   | awk '{print $1}' \
   | fgcz_bfabric_delete_workunits.py 
```

find empty resources file in bfabric
```{sh}
bfabric_list.py resource filechecksum `md5sum < /dev/null | cut -c-32` \
  | cat -n \
  | tail
```

## examples

### bash script generated by the yaml wrapper creator / submitter

externaljobid-45939_executableid-15312.bash listing:

```bash
#!/bin/bash
#
# $HeadURL: http://fgcz-svn.uzh.ch/repos/scripts/trunk/linux/bfabric/apps/python/README.md $
# $Id: README.md 2535 2016-10-24 08:49:17Z cpanse $
# Christian Panse <cp@fgcz.ethz.ch> 2007-2015

# Grid Engine Parameters
#$ -q PRX@fgcz-c-071
#$ -e /home/bfabric/sgeworker/logs/workunitid-134923_resourceid-203236.err
#$ -o /home/bfabric/sgeworker/logs/workunitid-134923_resourceid-203236.out


set -e
set -o pipefail

export EXTERNALJOBID=45938
export RESSOURCEID_OUTPUT=203238
export RESSOURCEID_STDOUT_STDERR="203237 203238"
export OUTPUT="bfabric@fgczdata.fgcz-net.unizh.ch:/srv/www/htdocs//p1000/bfabric/Proteomics/gerneric_yaml/2015/2015-09/2015-09-02//workunit_134923//203236.zip"

# job configuration set by B-Fabrics wrapper_creator executable
_OUTPUT=`echo $OUTPUT | cut -d"," -f1`
test $? -eq 0 && _OUTPUTHOST=`echo $_OUTPUT | cut -d":" -f1`
test $? -eq 0 && _OUTPUTPATH=`echo $_OUTPUT | cut -d":" -f2`
test $? -eq 0 && _OUTPUTPATH=`dirname $_OUTPUTPATH`
test $? -eq 0 && ssh $_OUTPUTHOST "mkdir -p $_OUTPUTPATH"

if [ $? -eq 1 ];
then
    echo "writting to output url failed!";
    exit 1;
fi

cat > /tmp/yaml_config.$$ <<EOF
application:
  input:
    mascot_dat:
    - bfabric@fgcz-s-018.uzh.ch//usr/local/mascot/:/data/20150807/F221967.dat
    - bfabric@fgcz-s-018.uzh.ch//usr/local/mascot/:/data/20150807/F221973.dat
  output:
  - bfabric@fgczdata.fgcz-net.unizh.ch:/srv/www/htdocs//p1000/bfabric/Proteomics/gerneric_yaml/2015/2015-09/2015-09-02//workunit_134923//203236.zip
  parameters:
    gelcms: 'true'
    mudpit: 'false'
    qmodel: None
    xtandem: 'false'
  protocol: scp
job_configuration:
  executable: /usr/local/fgcz/proteomics/bin/fgcz_scaffold.bash
  external_job_id: 45938
  input:
    mascot_dat:
    - 201919
    - 201918
  output:
    protocol: scp
    resource_id: 203238
    ssh_args: -o StrictHostKeyChecking=no -c arcfour -2 -l bfabric -x
  stderr:
    protocol: file
    resource_id: 203237
    url: /home/bfabric/sgeworker/logs/workunitid-134923_resourceid-203236.err
  stdout:
    protocol: file
    resource_id: 203238
    url: /home/bfabric/sgeworker/logs/workunitid-134923_resourceid-203236.out
  workunit_id: 134923

EOF

# debug / host statistics
hostname
uptime
echo $0
pwd

# run the application
test -f /tmp/yaml_config.$$ && /usr/local/fgcz/proteomics/bin/fgcz_scaffold.bash /tmp/yaml_config.$$

if [ $? -eq 0 ];
then
    /home/bfabric/.python/fgcz_bfabric_setResourceStatus_available.py $RESSOURCEID_OUTPUT
    /home/bfabric/.python/fgcz_bfabric_setExternalJobStatus_done.py $EXTERNALJOBID
else
    echo "application failed"
    /home/bfabric/.python/fgcz_bfabric_setResourceStatus_available.py $RESSOURCEID_STDOUT_STDERR $RESSOURCEID;
    exit 1;
fi


# should be available also as zero byte files

/home/bfabric/.python/fgcz_bfabric_setResourceStatus_available.py $RESSOURCEID_STDOUT_STDERR

exit 0
```

### curl example

```
cat ~/query.xml 
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:end="http://endpoint.webservice.component.bfabric.org/">
   <soapenv:Header/>
   <soapenv:Body>
      <end:read>
         <parameters>
            <login>cpanse</login>
<password>$2a$10$UXXXL1lr0wwp0cnByu0SXuxxxhakhjfskjhdgskhnSk7gBIUvy/au</password>

            <query>

               <status>pending</status>
            </query>
         </parameters>
      </end:read>
   </soapenv:Body>
</soapenv:Envelope> 

test $? -eq 0 \
&& curl --header "Content-Type: text/xml;charset=UTF-8" \
--header "SOAPAction: ACTION_YOU_WANT_TO_CALL" \
--data @query.xml \
http://fgcz-bfabric.uzh.ch/bfabric/workunit?wsdl
```


### Example usage

remove accidentally inserted mgf files

```
bfabric_list.py importresource \
  | grep mgf$ \
  | awk '{print $1}' \
  | tee /tmp/$$.log \
  | while read i; 
  do 
    bfabric_delete.py importresource $i ; 
  done
```
