#
# TODO:
#		- add pwc module (with hooks for pwcx)
#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
%define		_rel	3
Summary:	PWCX - decompressor modules for Philips USB webcams
Summary(pl):	PWCX - modu³y dekompresuj±ce obraz z kamer internetowych Philipsa
Name:		pwcx
Version:	9.0
Release:	%{_rel}
License:	Philips B.V.
Group:		Applications/Multimedia
Source0:	http://www.smcc.demon.nl/webcam/%{name}-%{version}.tar.gz
# Source0-md5:	73907e7e1ae7c311553182569ce6ab1c
Source1:	%{name}-Makefile
URL:		http://www.smcc.demon.nl/webcam/
%if %{with kernel}
%if %{with dist_kernel}
BuildRequires:	kernel-module-build >= 3:2.6.7
BuildRequires:	kernel-source
%endif
BuildRequires:	rpmbuild(macros) >= 1.153
%endif
BuildRequires:	pkgconfig
%if %{with userspace}
BuildRequires:	qmake
BuildRequires:	qt-devel
%endif
ExclusiveArch:	%{ix86} ia64 ppc
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Decompresor module for Philips webcams, this allows you to use higher
resoluwion and framerate. Working cameras: Philips: PCA645VC and
646VC, "Vesta", "Vesta Pro", "Vesta Scan", "ToUCam XS" (PCVC720K/40,
/20 is supported by ov511), "ToUCam Fun", "ToUCam Pro", "ToUCam Scan",
"ToUCam II", "ToUCam Pro II"; Askey VC010; Creative Labs Webcam: 5
(the old one; USB Product ID: 0x400C) and Pro Ex Logitech QuickCam
3000 Pro, 4000 Pro, Notebook Pro, Zoom and Orbit/Sphere; Samsung
MPC-C10 and MPC-C30; Sotec Afina Eye; Visionite VCS UM100 and VCS
UC300.

%description -l pl
Modu³ dekompresuj±cy obraz z kamer na uk³adzie Philipsa. Pozwala na
uzyskanie wiêkszej rozdzielczo¶ci i ilo¶ci klatek. Obs³ugiwane kamery:
Philips: PCA645VC and 646VC, "Vesta", "Vesta Pro", "Vesta Scan",
"ToUCam XS" (PCVC720K/40, K/20 dzia³a z ov511), "ToUCam Fun", "ToUCam
Pro", "ToUCam Scan", "ToUCam II", "ToUCam Pro II"; Askey VC010;
Creative Labs Webcam: 5 (stary typ; USB Product ID: 0x400C) i Pro Ex
Logitech QuickCam 3000 Pro, 4000 Pro, Notebook Pro, Zoom i
Orbit/Sphere; Samsung MPC-C10 and MPC-C30; Sotec Afina Eye; Visionite
VCS UM100 i VCS UC300.

%package -n kernel-video-pwcx
Summary:	Linux driver for Philips USB webcams
Summary(pl):	Sterownik dla Linuksa do kamer internetowych Philipsa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel}

%description -n kernel-video-pwcx
This is driver for Philips USB webcams for Linux.

This package contains Linux module.

%description -n kernel-video-pwcx -l pl
Sterownik dla Linuksa do kamer internetowych Philipsa.

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-video-pwcx
Summary:	Linux SMP driver for Philips USB webcams
Summary(pl):	Sterownik dla Linuksa SMP do kamer internetowych Philipsa
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel-smp}

%description -n kernel-smp-video-pwcx
This is driver for Philips USB webcams for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-video-pwcx -l pl
Sterownik dla Linuksa do kamer internetowych Philipsa.

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q

%build
cd pwcx
%ifarch %{ix86}
ln -sf ../x86/libpwcx.a libpwcx.a
%endif
%ifarch ia64
ln -sf ../x86_64/libpwcx.a libpwcx.a
%endif
%ifarch ppc
ln -sf ../powerpc/libpwcx.a libpwcx.a
%endif
cd -

%if %{with userspace}
cd testpwcx
qmake
%{__make} \
	QTDIR=%{_prefix} \
	CXXFLAGS="%{rpmcflags} %(pkg-config --cflags qt-mt)" \
	LDFLAGS="%{rpmldflags}" \
	SUBLIBS="-L../pwcx"
cd -
%endif

%if %{with kernel}
# kernel module(s)
cd pwcx
install %{SOURCE1} Makefile
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
	if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
		exit 1
	fi
	rm -rf include
	install -d include/{linux,config}
	ln -sf %{_kernelsrcdir}/config-$cfg .config
	ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
	ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
	ln -sf %{_kernelsrcdir}/Module.symvers-$cfg Module.symvers
	touch include/config/MARKER
	%{__make} -C %{_kernelsrcdir} clean \
		RCS_FIND_IGNORE="-name '*.ko' -o" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	%{__make} -C %{_kernelsrcdir} modules \
		CC="%{__cc}" CPP="%{__cpp}" \
		M=$PWD O=$PWD \
		%{?with_verbose:V=1}
	mv pwcx{,-$cfg}.ko
done
cd -
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_bindir}
install testpwcx/testpwcx $RPM_BUILD_ROOT%{_bindir}/pwcx-test
%endif

%if %{with kernel}
cd pwcx
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/drivers/usb/media
install pwcx-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/drivers/usb/media/pwcx.ko
%if %{with smp} && %{with dist_kernel}
install pwcx-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/drivers/usb/media/pwcx.ko
%endif
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-video-pwcx
%depmod %{_kernel_ver}

%postun -n kernel-video-pwcx
%depmod %{_kernel_ver}

%post -n kernel-smp-video-pwcx
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-video-pwcx
%depmod %{_kernel_ver}smp

%if %{with kernel}
%files -n kernel-video-pwcx
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/drivers/usb/media/pwcx.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-video-pwcx
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/drivers/usb/media/pwcx.ko*
%endif
%endif

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README
%attr(755,root,root) %{_bindir}/pwcx-test
%endif
