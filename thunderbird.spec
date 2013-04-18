Summary:	E-mail client
Name:		thunderbird
Version:	17.0.5
Release:	1
License:	MPL v1.1 or GPL v2+ or LGPL v2.1+
Group:		X11/Applications
Source0:	http://releases.mozilla.org/pub/mozilla.org/%{name}/releases/%{version}/source/%{name}-%{version}.source.tar.bz2
# Source0-md5:	609a11ce7bb246cebf67d993a035ca52
Source1:	http://releases.mozilla.org/pub/mozilla.org/%{name}/releases/%{version}/linux-i686/xpi/de.xpi
# Source1-md5:	e81e63d8fac6c61cbbe72b1c8b0ce05c
Source2:	http://releases.mozilla.org/pub/mozilla.org/%{name}/releases/%{version}/linux-i686/xpi/pl.xpi
# Source2-md5:	8fc0aea02c1373f0ac0b7fa7eac2fa0c
Source100:	vendor.js
Patch0:		%{name}-install-dir.patch
Patch1:		firefox-hunspell.patch
Patch2:		firefox-system-cairo.patch
Patch3:		firefox-virtualenv.patch
Patch4:		xulrunner-gyp-slashism.patch
URL:		http://www.mozilla.org/projects/firefox/
BuildRequires:	GConf-devel
BuildRequires:	OpenGL-devel
BuildRequires:	automake
BuildRequires:	bzip2-devel
BuildRequires:	cairo-devel >= 1.10.2-2
BuildRequires:	gtk+-devel
BuildRequires:	hunspell-devel
BuildRequires:	libIDL-devel
BuildRequires:	libevent-devel
BuildRequires:	libffi-devel
BuildRequires:	libjpeg-devel
BuildRequires:	libnotify-devel
BuildRequires:	libpng-devel
BuildRequires:	libstdc++-devel
BuildRequires:	libvpx-devel
BuildRequires:	nspr-devel >= 1:4.9
BuildRequires:	nss-devel >= 1:3.13.3
BuildRequires:	pango-devel
BuildRequires:	perl-modules
BuildRequires:	pkg-config
BuildRequires:	sed
BuildRequires:	sqlite3-devel >= 3.7.10
BuildRequires:	startup-notification-devel
BuildRequires:	xorg-libXcursor-devel
BuildRequires:	xorg-libXft-devel
BuildRequires:	zip
BuildRequires:	zlib-devel
Requires(post,postun):	desktop-file-utils
Requires(post,postun):	/usr/bin/gtk-update-icon-cache
Requires(post,postun):	hicolor-icon-theme
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_noautoprovfiles	%{_libdir}/thunderbird/components
%define		_noautoprov		libmozjs.so libxpcom.so libxul.so
%define		_noautoreq		libmozjs.so libxpcom.so libxul.so

# bug680547
%define		specflags	-mno-avx

%description
E-mail client.

%prep
%setup -qc

cd comm-esr17
%patch0 -p1
%patch2 -p1

cd mozilla
%patch1 -p1
%patch3 -p1
%patch4 -p2

# use system headers
rm -f extensions/spellcheck/hunspell/src/*.hxx
echo 'LOCAL_INCLUDES += $(MOZ_HUNSPELL_CFLAGS)' >> extensions/spellcheck/src/Makefile.in

# find ../../dist/sdk -name "*.pyc" | xargs rm
# rm: missing operand
sed -i -e "s|xargs rm|xargs rm -f|g" toolkit/mozapps/installer/packager.mk

%build
cd comm-esr17
cp -f %{_datadir}/automake/config.* build/autoconf

cat << 'EOF' > .mozconfig
mk_add_options MOZ_OBJDIR=@TOPSRCDIR@/obj-%{_target_cpu}
mk_add_options MOZ_CO_PROJECT=mail
#
ac_add_options --enable-application=mail
#
ac_add_options --host=%{_host}
ac_add_options --build=%{_host}
#
ac_add_options --libdir=%{_libdir}
ac_add_options --prefix=%{_prefix}
#
ac_add_options --disable-crashreporter
ac_add_options --disable-installer
ac_add_options --disable-javaxpcom
ac_add_options --disable-logging
ac_add_options --disable-mochitest
ac_add_options --disable-tests
ac_add_options --disable-updater
#
ac_add_options --enable-safe-browsing
#
ac_add_options --disable-debugOp
ac_add_options --disable-pedantic
ac_add_options --disable-strip
ac_add_options --disable-strip-install
#
ac_add_options --enable-optimize
#
ac_add_options --disable-gnomeui
ac_add_options --disable-gnomevfs
ac_add_options --enable-gio
ac_add_options --enable-startup-notification
#
ac_add_options --enable-system-cairo
ac_add_options --enable-system-hunspell
ac_add_options --enable-system-lcms
ac_add_options --enable-system-sqlite
ac_add_options --enable-system-ffi
ac_add_options --enable-system-pixman
ac_add_options --with-pthreads
ac_add_options --with-system-bz2
ac_add_options --with-system-jpeg
ac_add_options --with-system-libevent
ac_add_options --with-system-libvpx
ac_add_options --with-system-nspr
ac_add_options --with-system-nss
ac_add_options --with-system-png
ac_add_options --with-system-zlib
#
ac_add_options --enable-official-branding
#
export BUILD_OFFICIAL=1
export MOZILLA_OFFICIAL=1
mk_add_options BUILD_OFFICIAL=1
mk_add_options MOZILLA_OFFICIAL=1

EOF

export CFLAGS="%(echo %{rpmcflags} | sed 's/ -g2/ -g1/g')"
export CXXFLAGS="%(echo %{rpmcxxflags} | sed 's/ -g2/ -g1/g')"
export LDFLAGS="%{rpmldflags} -Wl,-rpath,%{_libdir}/thunderbird"

%{__make} -f client.mk build		\
	CC="%{__cc}"			\
	CXX="%{__cxx}"			\
	MOZ_MAKE_FLAGS=%{?_smp_mflags}	\
	STRIP="/bin/true"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_bindir},%{_desktopdir}}	\
	$RPM_BUILD_ROOT%{_iconsdir}/hicolor/{16x16,22x22,24x24,32x32,48x48,256x256}/apps

cd comm-esr17

%{__make} -j1 -f client.mk install		\
	DESTDIR=$RPM_BUILD_ROOT		\
	STRIP="/bin/true"

install %{SOURCE1} $RPM_BUILD_ROOT%{_libdir}/%{name}/extensions/langpack-de@firefox.mozilla.org.xpi
install %{SOURCE2} $RPM_BUILD_ROOT%{_libdir}/%{name}/extensions/langpack-pl@firefox.mozilla.org.xpi

install %{SOURCE100} $RPM_BUILD_ROOT%{_libdir}/%{name}/defaults/pref

%{__rm} -r $RPM_BUILD_ROOT%{_libdir}/%{name}/dictionaries

ln -s %{_datadir}/myspell $RPM_BUILD_ROOT%{_libdir}/%{name}/dictionaries
ln -s %{_datadir}/myspell $RPM_BUILD_ROOT%{_libdir}/%{name}/hyphenation

ln -s %{_libdir}/browser-plugins $RPM_BUILD_ROOT%{_libdir}/%{name}/plugins

for i in 16 22 24 32 48 256; do
    install -d $RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps
    cp other-licenses/branding/thunderbird/mailicon${i}.png \
    	$RPM_BUILD_ROOT%{_datadir}/icons/hicolor/${i}x${i}/apps/thunderbird.png
done

cat > $RPM_BUILD_ROOT%{_desktopdir}/%{name}.desktop <<EOF
[Desktop Entry]
Name=Thunderbird
GenericName=Mail Client
Comment=Mail
Exec=thunderbird %u
Icon=%{name}
StartupNotify=true
Terminal=false
Type=Application
Categories=GTK;Network;Email;
MimeType=message/rfc822;x-scheme-handler/mailto;
EOF

rm -f $RPM_BUILD_ROOT%{_bindir}/%{name}
ln -s %{_libdir}/%{name}/thunderbird-bin $RPM_BUILD_ROOT%{_bindir}/%{name}

rm -rf $RPM_BUILD_ROOT{%{_datadir}/idl,%{_includedir},%{_libdir}/thunderbird-devel*}

%clean
rm -rf $RPM_BUILD_ROOT

%post
%update_icon_cache hicolor
%update_desktop_database_post

%postun
%update_icon_cache hicolor
%update_desktop_database_postun

%files
%defattr(644,root,root,755)
%dir %{_libdir}/%{name}
%dir %{_libdir}/%{name}/components
%dir %{_libdir}/%{name}/defaults
%dir %{_libdir}/%{name}/defaults/pref
%dir %{_libdir}/%{name}/dictionaries
%dir %{_libdir}/%{name}/extensions
%dir %{_libdir}/%{name}/hyphenation
%dir %{_libdir}/%{name}/plugins

%attr(755,root,root) %{_bindir}/thunderbird
%attr(755,root,root) %{_libdir}/%{name}/thunderbird-bin
%attr(755,root,root) %{_libdir}/%{name}/components/libdbusservice.so
%attr(755,root,root) %{_libdir}/%{name}/components/libmozgnome.so
%attr(755,root,root) %{_libdir}/%{name}/libldap60.so
%attr(755,root,root) %{_libdir}/%{name}/libldif60.so
%attr(755,root,root) %{_libdir}/%{name}/libmozalloc.so
%attr(755,root,root) %{_libdir}/%{name}/libprldap60.so
%attr(755,root,root) %{_libdir}/%{name}/libxpcom.so
%attr(755,root,root) %{_libdir}/%{name}/libxul.so

%attr(755,root,root) %{_libdir}/%{name}/mozilla-xremote-client
%attr(755,root,root) %{_libdir}/%{name}/plugin-container
%{_libdir}/%{name}/platform.ini
%{_libdir}/%{name}/dependentlibs.list

%{_libdir}/%{name}/application.ini
%{_libdir}/%{name}/blocklist.xml
%{_libdir}/%{name}/chrome
%{_libdir}/%{name}/chrome.manifest
%{_libdir}/%{name}/components/binary.manifest
%{_libdir}/%{name}/defaults/messenger
%{_libdir}/%{name}/defaults/pref/channel-prefs.js
%{_libdir}/%{name}/defaults/pref/vendor.js
%{_libdir}/%{name}/extensions/{972ce4c6-7e08-4474-a285-3208198ce6fd}
%{_libdir}/%{name}/isp
%{_libdir}/%{name}/omni.ja
%{_libdir}/%{name}/searchplugins

%lang(de) %{_libdir}/%{name}/extensions/langpack-de@firefox.mozilla.org.xpi
%lang(pl) %{_libdir}/%{name}/extensions/langpack-pl@firefox.mozilla.org.xpi

%{_desktopdir}/%{name}.desktop
%{_iconsdir}/hicolor/*/apps/*.png

