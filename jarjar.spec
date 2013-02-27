Summary:	Jar Jar Links
Name:		jarjar
Version:	1.0
Release:	2.rc7.8
Epoch:		0
License:	GPL
URL:		http://code.google.com/p/jarjar/
Group:		Development/Java
Source0:	http://%{name}.googlecode.com/files/%{name}-src-1.0rc7.zip
Source1:	jarjar-0.9.pom
BuildRequires:	ant >= 0:1.6
BuildRequires:	ant-junit >= 0:1.6
BuildRequires:	java-rpmbuild >= 0:1.7.2
BuildRequires:	junit
BuildRequires:	asm3
BuildRequires:	maven2
BuildRequires:	java-1.6.0-openjdk-devel

Requires:	asm3
Requires(post):	jpackage-utils >= 0:1.7.2
Requires(postun):	jpackage-utils >= 0:1.7.2
BuildArch:	noarch


%description
Jar Jar Links is a utility that makes it easy to repackage Java 
libraries and embed them into your own distribution. This is 
useful for two reasons:
You can easily ship a single jar file with no external dependencies. 
You can avoid problems where your library depends on a specific 
version of a library, which may conflict with the dependencies of 
another library.

%package maven2-plugin
Summary:	Maven2 plugin for %{name}
Group:		Development/Java
Requires:	maven2
Requires:	%{name} = %EVRD

%description maven2-plugin
%{summary}.

%package javadoc
Summary:	Javadoc for %{name}
Group:		Development/Java

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
export JAVA_HOME=%_prefix/lib/jvm/java-1.6.0
ant jar jar-util javadoc mojo

%install

# jars
mkdir -p %{buildroot}%{_javadir}

install -m 644 dist/%{name}-%{version}rc7.jar \
  %{buildroot}%{_javadir}/%{name}-%{version}.jar
install -m 644 dist/%{name}-util-%{version}rc7.jar \
  %{buildroot}%{_javadir}/%{name}-util-%{version}.jar
install -m 644 dist/%{name}-plugin-%{version}rc7.jar \
  %{buildroot}%{_javadir}/%{name}-maven2-plugin-%{version}.jar

(cd %{buildroot}%{_javadir} && for jar in *-%{version}.jar; do ln -sf ${jar} `echo $jar| sed "s|-%{version}||g"`; done)

%add_to_maven_depmap tonic jarjar %{version} JPP %{name}
%add_to_maven_depmap com.tonicsystems jarjar %{version} JPP %{name}
%add_to_maven_depmap tonic jarjar-util %{version} JPP %{name}-util
%add_to_maven_depmap com.tonicsystems jarjar-util %{version} JPP %{name}-util
%add_to_maven_depmap tonic jarjar-plugin %{version} JPP %{name}-plugin
%add_to_maven_depmap com.tonicsystems jarjar-plugin %{version} JPP %{name}-plugin

# poms
install -d -m 755 %{buildroot}%{_datadir}/maven2/poms
install -pm 644 %{SOURCE1} \
    %{buildroot}%{_datadir}/maven2/poms/JPP.%{name}.pom

# javadoc
mkdir -p %{buildroot}%{_javadocdir}/%{name}-%{version}
cp -pr dist/javadoc/* %{buildroot}%{_javadocdir}/%{name}-%{version}
ln -s %{name}-%{version} %{buildroot}%{_javadocdir}/%{name}

%post
%update_maven_depmap

%postun
%update_maven_depmap

%files
%defattr(0644,root,root,0755)
%doc COPYING
%{_javadir}/%{name}-%{version}.jar
%{_javadir}/%{name}-util-%{version}.jar
%{_javadir}/%{name}.jar
%{_javadir}/%{name}-util.jar
%{_datadir}/maven2/poms/*
%config(noreplace) %{_mavendepmapfragdir}/*

%files maven2-plugin
%defattr(0644,root,root,0755)
%{_javadir}/%{name}-maven2-plugin-%{version}.jar
%{_javadir}/%{name}-maven2-plugin.jar

%files javadoc
%defattr(0644,root,root,0755)
%{_javadocdir}/%{name}-%{version}
%{_javadocdir}/%{name}
