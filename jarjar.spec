# Copyright (c) 2000-2007, JPackage Project
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the
#    distribution.
# 3. Neither the name of the JPackage Project nor the names of its
#    contributors may be used to endorse or promote products derived
#    from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
%define _with_gcj_support 1
%define gcj_support %{?_with_gcj_support:1}%{!?_with_gcj_support:%{?_without_gcj_support:0}%{!?_without_gcj_support:%{?_gcj_support:%{_gcj_support}}%{!?_gcj_support:0}}}

%define section free

Summary:        Jar Jar Links
Name:           jarjar
Version:        1.0
Release:        %mkrel 2.rc7.3
Epoch:          0
License:        GPL
URL:            http://code.google.com/p/jarjar/
Group:          Development/Java
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Source0:        http://%{name}.googlecode.com/files/%{name}-src-1.0rc7.zip
Source1:        jarjar-0.9.pom
BuildRequires:  ant >= 0:1.6
BuildRequires:  ant-junit >= 0:1.6
BuildRequires:  java-rpmbuild >= 0:1.7.2
BuildRequires:  junit
BuildRequires:  asm3
BuildRequires:  maven2

Requires:  asm3
Requires(post):    jpackage-utils >= 0:1.7.2
Requires(postun):  jpackage-utils >= 0:1.7.2
%if %{gcj_support}
BuildRequires:    java-gcj-compat-devel
%endif

%if ! %{gcj_support}
BuildArch:      noarch
%endif


%description
Jar Jar Links is a utility that makes it easy to repackage Java 
libraries and embed them into your own distribution. This is 
useful for two reasons:
You can easily ship a single jar file with no external dependencies. 
You can avoid problems where your library depends on a specific 
version of a library, which may conflict with the dependencies of 
another library.

%package maven2-plugin
Summary:        Maven2 plugin for %{name}
Group:          Development/Java
Requires:       maven2
Requires:       %{name} = %{epoch}:%{version}-%{release}

%description maven2-plugin
%{summary}.

%package javadoc
Summary:        Javadoc for %{name}
Group:          Development/Java

%description javadoc
%{summary}.

%prep
%setup -q -n %{name}-%{version}rc7
%remove_java_binaries

%build
pushd lib
ln -sf $(build-classpath asm3/asm3) asm-3.1.jar
ln -sf $(build-classpath asm3/asm3-commons) asm-commons-3.1.jar
ln -sf $(build-classpath maven2/plugin-api) maven-plugin-api.jar
popd
export CLASSPATH=$(build-classpath ant asm3/asm3 asm3/asm3-commons maven2/plugin-api)
%{ant} jar jar-util javadoc mojo

%install
rm -rf $RPM_BUILD_ROOT

# jars
mkdir -p $RPM_BUILD_ROOT%{_javadir}

install -m 644 dist/%{name}-%{version}rc7.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-%{version}.jar
install -m 644 dist/%{name}-util-%{version}rc7.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-util-%{version}.jar
install -m 644 dist/%{name}-plugin-%{version}rc7.jar \
  $RPM_BUILD_ROOT%{_javadir}/%{name}-maven2-plugin-%{version}.jar

(cd $RPM_BUILD_ROOT%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

%add_to_maven_depmap tonic jarjar %{version} JPP %{name}
%add_to_maven_depmap com.tonicsystems jarjar %{version} JPP %{name}
%add_to_maven_depmap tonic jarjar-util %{version} JPP %{name}-util
%add_to_maven_depmap com.tonicsystems jarjar-util %{version} JPP %{name}-util
%add_to_maven_depmap tonic jarjar-plugin %{version} JPP %{name}-plugin
%add_to_maven_depmap com.tonicsystems jarjar-plugin %{version} JPP %{name}-plugin

# poms
install -d -m 755 $RPM_BUILD_ROOT%{_datadir}/maven2/poms
install -pm 644 %{SOURCE1} \
    $RPM_BUILD_ROOT%{_datadir}/maven2/poms/JPP.%{name}.pom

# javadoc
mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
cp -pr dist/javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} $RPM_BUILD_ROOT%{_javadocdir}/%{name}

%if %{gcj_support}
%{_bindir}/aot-compile-rpm
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_maven_depmap
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%postun
%update_maven_depmap
%if %{gcj_support}
if [ -x %{_bindir}/rebuild-gcj-db ]
then
  %{_bindir}/rebuild-gcj-db
fi
%endif

%files
%defattr(0644,root,root,0755)
%doc COPYING
%{_javadir}/%{name}-%{version}.jar
%{_javadir}/%{name}-util-%{version}.jar
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-util.jar
%{_datadir}/maven2/poms/*
%config(noreplace) %{_mavendepmapfragdir}/*
%if %{gcj_support}
%dir %{_libdir}/gcj/%{name}
%attr(-,root,root) %{_libdir}/gcj/%{name}/%{name}*-%{version}.jar.*
%endif

%files maven2-plugin
%defattr(0644,root,root,0755)
%{_javadir}/%{name}-maven2-plugin-%{version}.jar
%{_javadir}/%{name}-maven2-plugin.jar

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}
