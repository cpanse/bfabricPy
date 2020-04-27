#!/usr/bin/env python3

# Christian Panse <cp@fgcz.ethz.ch>
# 20200424-1300

import sys
import os
import yaml
import hashlib
from optparse import OptionParser
from bfabric import Bfabric
import getopt

assert sys.version_info >= (3, 6)

BFABRICSTORAGEID = 2

def save_resource(projectid=None, resource_file=None, applicationid=None, read_stdin=False):

    bfapp = Bfabric()

    if read_stdin:
        try:
            print("reading stdin")
            description = sys.stdin.read()
        except:
            print("reading from stdin failed.")
            raise

    try:
        md5 = hashlib.md5(open(resource_file, 'rb').read()).hexdigest()
    except:
        print("computing file checksum failed.")
        raise

    resource = bfapp.read_object(endpoint='resource', obj={'filechecksum': md5})

    try:    
        print("resource(s) already exist.".format(resource[0]._id))
        resource = bfapp.save_object(endpoint='resource', obj={'id': resource[0]._id, 'description': description})
        print(resource)
        return
    except:
        pass


    try:
        workunit = bfapp.save_object(endpoint='workunit',
                                 obj={'name': "{}".format(os.path.basename(resource_file)),
                                      'projectid': projectid,
                                      'applicationid': applicationid})
        print(workunit)
    except:
        raise


    obj = {'workunitid': workunit[0]._id,
           'filechecksum': md5,
           'relativepath': "{}".format(resource_file),
           'name': os.path.basename(resource_file),
           'size': os.path.getsize(resource_file),
           'status': 'available',
           'description': description,
           'storageid': BFABRICSTORAGEID
           }


    resource = bfapp.save_object(endpoint='resource', obj=obj)
    print(resource)

    workunit = bfapp.save_object(endpoint='workunit',
                                 obj={'id': workunit[0]._id, 'status': 'available'})
    print(workunit)


def usage():
    print
    print("{} -p <projectid> -a <applicationid> -r <resourcefile>".format(os.path.basename(sys.argv[0])))
    print("{} -p <projectid> -a <applicationid> -r <resourcefile> - < <stdin>".format(
        os.path.basename(sys.argv[0])))
    print
    print("Example")
    print("{} -p 3000 -a 273 -r /srv/www/htdocs/p3061/Proteomics/Analysis/fragpipe/cpanse_20200424/DS32024.zip ".format(os.path.basename(sys.argv[0])))


if __name__ == "__main__":
    #resource_file = "/srv/www/htdocs/p3061/Proteomics/Analysis/fragpipe/cpanse_20200424/DS32024.zip"
    #save_resource(projectid=3061, resource_file=resource_file, applicationid=274)

    (projectid, applicationid, resourefile) = (None, None, None)
    read_stdin = False

    try:
        opts, args = getopt.getopt(sys.argv[1:],"hp:a:r:-", ["help", "projectid=", "applicationid=", "resourcefile="])
    except getopt.GetoptError:
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()
            sys.exit(0)
        if o in ("-"):
            read_stdin = True
        elif o in ("-p", "--projectid"):
            projectid = a
        elif o in ("-a", "--applicationid"):
            applicationid = a
        elif o in ("-r", "--resourcefile"):
            resourcefile = a
            try:
                os.path.isfile(resourcefile)
            except:
                print("can not access file '{}'".format(resourcefile))
                raise
        else:
            usage()
            assert False, "unhandled option"

    if projectid is None or resource_file is None or applicationid is None:
        print("at least one of the arguments is None.")
        usage()
        sys.exit(1)
