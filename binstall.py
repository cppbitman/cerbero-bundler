import os
import tarfile
import re




PKG_PATTERN=re.compile('(?P<name>\w+(-\w+)*)'
  +'-(?P<platform>(windows|linux))'
  +'-(?P<arch>(x86|x86_64))'
  +'-(?P<version>(\d+(.\d+)*(-\d+)*))'
  +'(-(?P<type>(devel|pdb|test)))?'
  +'(?P<debug>@debug)?'
  + '.tar.bz2')


class InstallError(Exception):
    header = ''
    msg = ''

    def __init__(self, msg=''):
        self.msg = msg
        Exception.__init__(self, self.header + msg)


class PKGConfig(object):

    def __init__(self, fobj):
        self._fobj = fobj
        self._prefix = None
        self._exec_prefix = None
        self._libdir = None
        self.sharedlibdir = None



PKGCONFIG_PATTERN=re.compile('(?P<name>(prefix|exec_prefix|libdir|includedir|sharedlibdir))'
  +'=(?P<value>((/\w+|\w://)?[^\*\?\"<>\|\r\n]+))'
  +'(?P<end>[\r\n])*')
class Installer(object):

    def __init__(self,prefix):
        self._prefix = prefix
    
    def _pkginfo(self,tarball):
        pkginfo= re.match( PKG_PATTERN, tarball)
        if not pkginfo:
            raise InstallError('invalied package name :%s'%tarball )
        
        pkginfo_dict=pkginfo.groupdict()
        if pkginfo_dict['type'] is None:
            pkginfo_dict['type'] = ''
        return pkginfo_dict
        

    def _repkgconfig(self, f ,fname):
        print '\n*',fname

        for line in f.readlines():
            m = re.match( PKGCONFIG_PATTERN , line )
            org={}
            new={}
            if not m :
                continue
                print m.group('name'),m.group('value'),'@%s@'%m.group('end')
            name  = m.group('name')
            value = m.group('value')
            org[name] = value
            if name == 'prefix':
                new[name] = value
            elif name == 'exec_prefix':
                if value == org.get('prefix'):
                    new[name] = '${prefix}'
                elif value.startswith('${prefix}'):
                    new[name] = value
                elif value.startswith(org.get('prefix')):
                    new[name] = value.replace(org['prefix'],'${prefix}')
                else:
                    pass#this is path need we guest the relationship with prefix

            #if m.group('name') == 'prefix':



    def install(self, tarball ):
        '''
        tarball - path of the package(tar.bz2)
        '''
        pkginfo= self._pkginfo(tarball)
        if not pkginfo:
            raise InstallError('invalied package name :%s'%tarball )

        if not os.path.isdir(self._prefix):
            os.makedirs( self._prefix )

        infod=os.path.join( self._prefix,'.install',pkginfo['name'],pkginfo['type'])

        if not os.path.isdir( infod ):
            os.makedirs( infod )
        
        try:
            tar = tarfile.open(tarball, "r:bz2")
            dirs=set()
            for i in tar.getnames():
                dirs.add( os.path.normpath(os.path.dirname(i)).replace('\\','/').lower() )
                
            for d in dirs:
                print '*', d
           # 
            #     



            #print '-----------------------'
            #for fname in tar.getnames():
            #    continue
            #    print fname
            #    continue
            #    if fname.endswith('.pc'):
            #        f= tar.extractfile( fname )
            #        self._repkgconfig( f ,fname)
            #        f.close()
            #    #tar.extract(file_name, target_path)
            tar.close()
        except Exception, e:
            raise Exception, e







if __name__ == '__main__':
    inst = Installer('.')
    inst.install('base-libs-windows-x86_64-1.12.0-devel.tar.bz2')








#tests=[ 'base-libs-windows-x86_64-1.12.0.tar.bz2',
#        'base-libs-windows-x86_64-1.12.0-devel.tar.bz2',
#        'base-libs-windows-x86-1.12.0-1-devel.tar.bz2' ,
#        'base-libs-windows-x86-1.12.0-1-devel@debug.tar.bz2' ]











#for pname in tests:
#    print '-----'
#    print pname#

#    m = re.match( PKG_PATTERN , pname )
#    print m
#    for k ,v in m.groupdict().iteritems():
#        print '    %s: %s'%(k,v)