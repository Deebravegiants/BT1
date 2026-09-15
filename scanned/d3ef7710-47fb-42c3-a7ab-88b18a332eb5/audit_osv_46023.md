# [H] JLSEC-2026-580

## Summary
Severity: High
Advisory: JLSEC-2026-580
Ecosystem: Julia
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/JLSEC-2026-580
Type: osv

## Affected
- Julia: `XSLT_jll` — affected >=0 <1.1.34+0

## Details
In xsltCopyText in transform.c in libxslt 1.1.33, a pointer variable isn't reset under certain circumstances. If the relevant memory area happened to be freed and reused in a certain way, a bounds check could fail and memory outside a buffer could be written to, or uninitialized data could be disclosed.

## References
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00010.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00015.html
- http://lists.opensuse.org/opensuse-security-announce/2020-02/msg00025.html
- http://lists.opensuse.org/opensuse-security-announce/2020-05/msg00062.html
- http://www.openwall.com/lists/oss-security/2019/11/17/2
- https://access.redhat.com/errata/RHSA-2020:0514
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15746
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15768
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=15914
- https://gitlab.gnome.org/GNOME/libxslt/commit/2232473733b7313d67de8836ea3b29eec6e8e285
- https://lists.debian.org/debian-lts-announce/2019/10/msg00037.html
- https://security.netapp.com/advisory/ntap-20191031-0004/
- https://security.netapp.com/advisory/ntap-20200416-0004/
- https://usn.ubuntu.com/4164-1/
- https://www.oracle.com/security-alerts/cpuapr2020.html
