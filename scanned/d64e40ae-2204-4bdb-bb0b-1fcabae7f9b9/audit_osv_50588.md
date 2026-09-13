# [H] CVE-2020-24972

## Summary
Severity: High
Advisory: CVE-2020-24972
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-08-29
Source: https://osv.dev/vulnerability/CVE-2020-24972
Type: osv

## Details
The Kleopatra component before 3.1.12 (and before 20.07.80) for GnuPG allows remote attackers to execute arbitrary code because openpgp4fpr: URLs are supported without safe handling of command-line options. The Qt platformpluginpath command-line option can be used to load an arbitrary DLL.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IRIPL72WMXTVWS2M7WYV5SNPETYJ2YI7/
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2020-10/msg00064.html
- https://security.gentoo.org/glsa/202008-21
- https://dev.gnupg.org/rKLEOPATRAb4bd63c1739900d94c04da03045e9445a5a5f54b
- https://dev.gnupg.org/source/kleo/browse/master/CMakeLists.txt
