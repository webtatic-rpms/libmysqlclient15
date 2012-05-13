Name: libmysqlclient15
Version: 5.0.77
Release: 1.1%{?dist}
Summary: MySQL shared libraries
Group: Applications/Databases
URL: http://www.mysql.com
# exceptions allow client libraries to be linked with most open source SW,
# not only GPL code.
License: GPLv2 with exceptions

Source0: http://dev.mysql.com/get/Downloads/MySQL-5.0/mysql-%{version}.tar.gz
Source4: scriptstub.c
Source5: my_config.h
# Working around perl dependency checking bug in rpm FTTB. Remove later.
Source999: filter-requires-mysql.sh 
Patch1: mysql-libdir.patch
Patch2: mysql-errno.patch
Patch3: mysql-stack.patch
Patch4: mysql-testing.patch
Patch5: mysql-no-atomic.patch
Patch6: mysql-rpl_ddl.patch
Patch7: mysql-rpl-test.patch
Patch8: mysql-install-test.patch
Patch9: mysql-bdb-link.patch
Patch10: mysql-strmov.patch
Patch11: mysql-html-bug.patch
Patch13: mysql-no-dbug.patch
Patch15: mysql-stack-guard.patch
Patch16: mysql-expired-certs.patch
Patch17: mysql-format-string.patch
Patch18: mysql-name-const.patch
Patch19: mysql-cve-2009-4019.patch
Patch20: mysql-cve-2009-4028.patch
Patch21: mysql-cve-2009-4030.patch
Patch22: mysql-cve-2010-1626.patch
Patch23: mysql-cve-2010-1848_1850.patch
Patch24: mysql-cve-2010-3677.patch
Patch25: mysql-cve-2010-3680.patch
Patch26: mysql-cve-2010-3681.patch
Patch27: mysql-cve-2010-3682.patch
Patch28: mysql-cve-2010-3833.patch
Patch29: mysql-cve-2010-3835.patch
Patch30: mysql-cve-2010-3836.patch
Patch31: mysql-cve-2010-3837.patch
Patch32: mysql-cve-2010-3838.patch
Patch33: mysql-cve-2010-3839.patch
Patch34: mysql-cve-2010-3840.patch

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
Prereq: /sbin/ldconfig, /sbin/install-info, grep, fileutils
BuildRequires: gperf, perl, readline-devel, openssl-devel
BuildRequires: gcc-c++, ncurses-devel, zlib-devel
BuildRequires: libtool automake autoconf gawk

Requires: bash

# Working around perl dependency checking bug in rpm FTTB. Remove later.
%define __perl_requires %{SOURCE999}

# Force include and library files into a nonstandard place
%{expand: %%define _origincludedir %{_includedir}}
%{expand: %%define _origlibdir %{_libdir}}
%define _includedir %{_origincludedir}/%{name}
%define _libdir %{_origlibdir}/%{name}

%description
The libmysqlclient15 package provides the essential shared libraries for any 
MySQL client program or interface. You will need to install this package
to use any other MySQL package or any clients that need to connect to a
MySQL server.

%package devel

Summary: Files for development of MySQL applications
Group: Applications/Databases
Requires: %{name} = %{version}-%{release}
Requires: openssl-devel
Conflicts: MySQL-devel

%description devel
MySQL is a multi-user, multi-threaded SQL database server. This
package contains the libraries and header files that are needed for
developing MySQL client applications.

%prep
%setup -q -n mysql-%{version}

%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1
%patch10 -p1
%patch11 -p1
%patch13 -p1
%patch15 -p1
%patch16 -p1
%patch17 -p1
%patch18 -p1
%patch19 -p1
%patch20 -p1
%patch21 -p1
%patch22 -p1
%patch23 -p1
%patch24 -p1
%patch25 -p1
%patch26 -p1
%patch27 -p1
%patch28 -p1
%patch29 -p1
%patch30 -p1
%patch31 -p1
%patch32 -p1
%patch33 -p1
%patch34 -p1

libtoolize --force
aclocal
automake --add-missing
autoconf
autoheader

%build
CFLAGS="%{optflags} -D_GNU_SOURCE -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE"
# MySQL 4.1.10 definitely doesn't work under strict aliasing; also,
# gcc 4.1 breaks MySQL 5.0.16 without -fwrapv
CFLAGS="$CFLAGS -fno-strict-aliasing -fwrapv"
%ifarch alpha
# Can't link C++ objects into an executable without this. Odd!
# -ECL 2002-12-19
CFLAGS="$CFLAGS -fPIC"
%endif
# Temporary workaround for gcc bug (bz #193912)
%ifarch s390x
CFLAGS="$CFLAGS -mtune=z900"
%endif
CXXFLAGS="$CFLAGS -fno-rtti -fno-exceptions"
export CFLAGS CXXFLAGS

%configure \
	--with-readline \
	--with-openssl \
	--without-debug \
	--enable-shared \
	--without-bench \
	--without-server \
	--without-docs \
	--without-man \
	--localstatedir=/var/lib/mysql \
	--with-unix-socket-path=/var/lib/mysql/mysql.sock \
	--with-mysqld-user="mysql" \
	--with-extra-charsets=all \
	--enable-local-infile \
	--enable-largefile \
	--enable-thread-safe-client \
	--disable-dependency-tracking \
	--with-named-thread-libs="-lpthread"

gcc $CFLAGS $LDFLAGS -o scriptstub "-DLIBDIR=\"%{_libdir}/mysql\"" %{SOURCE4}

# Not enabling assembler

make %{?_smp_mflags}
make check

%install
rm -rf $RPM_BUILD_ROOT

%makeinstall

# multilib header hack
# we only apply this to known Red Hat multilib arches, per bug #181335
case `uname -i` in
  i386 | x86_64 | ppc | ppc64 | s390 | s390x)
    install -m 644 include/my_config.h $RPM_BUILD_ROOT%{_includedir}/mysql/my_config_`uname -i`.h
    install -m 644 %{SOURCE5} $RPM_BUILD_ROOT%{_includedir}/mysql/
    ;;
  *)
    ;;
esac

mv ${RPM_BUILD_ROOT}%{_bindir}/mysql_config ${RPM_BUILD_ROOT}%{_libdir}/mysql/mysql_config

# We want the .so files both in regular _libdir (for execution) and
# in special _libdir/mysql4 directory (for convenient building of clients).
# The ones in the latter directory should be just symlinks though.
mkdir -p ${RPM_BUILD_ROOT}%{_origlibdir}/mysql
pushd ${RPM_BUILD_ROOT}%{_origlibdir}/mysql
mv -f ${RPM_BUILD_ROOT}%{_libdir}/mysql/libmysqlclient.so.15.*.* .
mv -f ${RPM_BUILD_ROOT}%{_libdir}/mysql/libmysqlclient_r.so.15.*.* .
cp -p -d ${RPM_BUILD_ROOT}%{_libdir}/mysql/libmysqlclient*.so.* .
popd
pushd ${RPM_BUILD_ROOT}%{_libdir}/mysql
ln -s ../../mysql/libmysqlclient.so.15.*.* .
ln -s ../../mysql/libmysqlclient_r.so.15.*.* .
popd

rm -rf $RPM_BUILD_ROOT%{_prefix}/mysql-test
rm -f ${RPM_BUILD_ROOT}%{_libdir}/mysql/*.{a,la}
rm -rf $RPM_BUILD_ROOT%{_datadir}/mysql
rm -rf $RPM_BUILD_ROOT%{_bindir}

mkdir -p $RPM_BUILD_ROOT/etc/ld.so.conf.d
echo "%{_origlibdir}/mysql" > $RPM_BUILD_ROOT/etc/ld.so.conf.d/%{name}-%{_arch}.conf

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig

%postun
if [ $1 = 0 ] ; then
    /sbin/ldconfig
fi

%files
%defattr(-,root,root)
%doc README COPYING EXCEPTIONS-CLIENT
%{_origlibdir}/mysql/libmysqlclient*.so.*
/etc/ld.so.conf.d/*

%files devel
%defattr(-,root,root)
%{_includedir}/mysql
%{_libdir}/mysql/libmysqlclient*.so
%{_libdir}/mysql/libmysqlclient*.so.*
%{_libdir}/mysql/mysql_config

%changelog
* Sat Feb 19 2011 Andy Thompson <andy@webtatic.com> 5.9.77-1.1
- rebuild for repository recovery

* Mon Dec 20 2010 Andy Thompson <andy@webtatic.com> 5.0.77-1
- Initial build
