#
# Conditional build:
%bcond_without	dist_kernel	# allow non-distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace module
%bcond_with	verbose		# verbose build (V=1)
#
Summary:	PWCX - decompressor modules for Philips USB webcams
Summary(pl):	PWCX - modu³y dekompresuj±ce obraz dla kamer internetowych Philipsa
Name:		pwcx
Version:	9.0
Release:	0.1
License:	based on an NDA and closed source
Group:		Applications/Multimedia
Source0:	http://www.smcc.demon.nl/webcam/%{name}-%{version}.tar.gz
# Source0-md5:	73907e7e1ae7c311553182569ce6ab1c
Source1:	%{name}-Makefile
URL:		http://www.smcc.demon.nl/webcam
%if %{with kernel}
%if %{with dist_kernel}
BuildRequires:	kernel-module-build >= 2.6.7
BuildRequires:	kernel-source
%endif
BuildRequires:	rpmbuild(macros) >= 1.153
%endif
#BuildRequires:	qt-devel
ExclusiveArch:	%{ix86} amd64
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
The decompressor modules are a plugin for the PWC core driver, and
gives you larger images and higher framerates with the webcams.

%description -l pl
- --pusty--

%package -n kernel-video-pwcx
Summary:	Linux driver for Philips USB webcams
Summary(pl):	Sterownik dla Linuksa do ...
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel}

%description -n kernel-video-pwcx
This is driver for Philips USB webcams for Linux.

This package contains Linux module.

%description -n kernel-video-pwcx -l pl
Sterownik dla Linuksa do ...

Ten pakiet zawiera modu³ j±dra Linuksa.

%package -n kernel-smp-video-pwcx
Summary:	Linux SMP driver for Philips USB webcams
Summary(pl):	Sterownik dla Linuksa SMP do ...
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
%{?with_dist_kernel:Requires(postun):	kernel-smp}

%description -n kernel-smp-video-pwcx
This is driver for Philips USB webcams for Linux.

This package contains Linux SMP module.

%description -n kernel-smp-video-pwcx -l pl
Sterownik dla Linuksa do ...

Ten pakiet zawiera modu³ j±dra Linuksa SMP.

%prep
%setup -q

%build
%if %{with userspace}

%endif

%if %{with kernel}
# kernel module(s)
cd pwcx
install %{SOURCE1} Makefile
%ifarch %{ix86}
ln -sf ../x86/libpwcx.a libpwcx.a
%endif
%ifarch amd64
ln -sf ../x86_64/libpwcx.a libpwcx.a
%endif

for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
    if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
	exit 1
    fi
    rm -rf include
    install -d include/{linux,config}
    ln -sf %{_kernelsrcdir}/config-$cfg .config
    ln -sf %{_kernelsrcdir}/include/linux/autoconf-$cfg.h include/linux/autoconf.h
    ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
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
%dos README
%endif
