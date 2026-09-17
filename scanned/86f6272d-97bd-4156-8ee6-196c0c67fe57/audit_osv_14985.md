# [H] CVE-2019-12816

## Summary
Severity: High
Advisory: CVE-2019-12816
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-06-15
Source: https://osv.dev/vulnerability/CVE-2019-12816
Type: osv

## Details
Modules.cpp in ZNC before 1.7.4-rc1 allows remote authenticated non-admin users to escalate privileges and execute arbitrary code by loading a module with a crafted name.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-07/msg00037.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00018.html
- https://lists.debian.org/debian-lts-announce/2019/06/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/4O24TQOB73X57GACLZVMRVUK4UKHLE5G/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/NHR6OD52FQAG5ZPZ42NJM2T765C3V2XC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TEESIGRNFLZUWXZPDGXAZ7JZTHYBDJ7G/
- https://usn.ubuntu.com/4044-1/
- https://seclists.org/bugtraq/2019/Jun/23
- https://security.gentoo.org/glsa/201908-15
- https://github.com/znc/znc/commit/8de9e376ce531fe7f3c8b0aa4876d15b479b7311
- https://github.com/znc/znc/compare/be1b6bc...d1997d6
