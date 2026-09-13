# [C] JLSEC-2026-577

## Summary
Severity: Critical
Advisory: JLSEC-2026-577
Ecosystem: Julia
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-577
Type: osv

## Affected
- Julia: `XSLT_jll` — affected >=0 <1.1.34+0

## Details
libxslt through 1.1.33 allows bypass of a protection mechanism because callers of xsltCheckRead and xsltCheckWrite permit access even upon receiving a -1 error code. xsltCheckRead can return -1 for a crafted URL that is not actually invalid and is subsequently loaded.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00048.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00052.html
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00053.html
- http://lists.opensuse.org/opensuse-security-announce/2019-06/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2019-08/msg00001.html
- http://www.openwall.com/lists/oss-security/2019/04/22/1
- http://www.openwall.com/lists/oss-security/2019/04/23/5
- https://gitlab.gnome.org/GNOME/libxslt/commit/e03553605b45c88f0b4b2980adfbbb8f6fca2fd6
- https://lists.debian.org/debian-lts-announce/2019/04/msg00016.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/36TEYN37XCCKN2XUMRTBBW67BPNMSW4K/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/GCOAX2IHUMKCM3ILHTMGLHCDSBTLP2JU/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/SK4YNISS22MJY22YX5I6V2U63QZAUEHA/
- https://security.netapp.com/advisory/ntap-20191017-0001/
- https://usn.ubuntu.com/3947-1/
- https://usn.ubuntu.com/3947-2/
- https://www.oracle.com/technetwork/security-advisory/cpuoct2019-5072832.html
