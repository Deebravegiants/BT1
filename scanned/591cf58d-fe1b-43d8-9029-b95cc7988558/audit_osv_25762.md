# [M] Libx11: out-of-bounds memory access in _xkbreadkeysyms()

## Summary
Severity: Medium
Advisory: CVE-2023-43785
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2023-10-10
Source: https://osv.dev/vulnerability/CVE-2023-43785
Type: osv

## Details
A vulnerability was found in libX11 due to a boundary condition within the _XkbReadKeySyms() function. This flaw allows a local user to trigger an out-of-bounds read error and read the contents of memory on the system.

## References
- https://access.redhat.com/downloads/content/package-browser/
- https://lists.debian.org/debian-lts-announce/2023/10/msg00004.html
- https://access.redhat.com/errata/RHSA-2024:2145
- https://access.redhat.com/errata/RHSA-2024:2973
- https://access.redhat.com/security/cve/CVE-2023-43785
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43785.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-43785
- https://security.netapp.com/advisory/ntap-20231103-0006/
- https://bugzilla.redhat.com/show_bug.cgi?id=2242252
- https://gitlab.freedesktop.org/xorg/lib/libx11
