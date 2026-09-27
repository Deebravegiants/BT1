# [H] CVE-2019-7443

## Summary
Severity: High
Advisory: CVE-2019-7443
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-07
Source: https://osv.dev/vulnerability/CVE-2019-7443
Type: osv

## Details
KDE KAuth before 5.55 allows the passing of parameters with arbitrary types to helpers running as root over DBus via DBusHelperProxy.cpp. Certain types can cause crashes, and trigger the decoding of arbitrary images with dynamically loaded plugins. In other words, KAuth unintentionally causes this plugin code to run as root, which increases the severity of any possible exploitation of a plugin vulnerability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DAWLQKTUQJOAPXOFWJQAQCA4LVM2P45F/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/PXVUJNXB6QKGPT6YJPJSG3U2BIR5XK5Y/
- http://lists.opensuse.org/opensuse-security-announce/2019-02/msg00060.html
- http://lists.opensuse.org/opensuse-security-announce/2019-02/msg00065.html
- https://bugzilla.suse.com/show_bug.cgi?id=1124863
- https://cgit.kde.org/kauth.git/commit/?id=fc70fb0161c1b9144d26389434d34dd135cd3f4a
