# [M] CVE-2021-25219

## Summary
Severity: Medium
Advisory: CVE-2021-25219
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2021-10-27
Source: https://osv.dev/vulnerability/CVE-2021-25219
Type: osv

## Details
In BIND 9.3.0 -> 9.11.35, 9.12.0 -> 9.16.21, and versions 9.9.3-S1 -> 9.11.35-S1 and 9.16.8-S1 -> 9.16.21-S1 of BIND Supported Preview Edition, as well as release versions 9.17.0 -> 9.17.18 of the BIND 9.17 development branch, exploitation of broken authoritative servers using a flaw in response processing can cause degradation in BIND resolver performance. The way the lame cache is currently designed makes it possible for its internal data structures to grow almost infinitely, which may cause significant delays in client query processing.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EF4NAVRV4H3W4GA3LGGZYUKD3HSJBAVW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YGV7SA27CTYLGFJSPUM3V36ZWK7WWDI4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YTKC4E3HUOLYN5IA4EBL4VAQSWG2ZVTX/
- https://kb.isc.org/v1/docs/cve-2021-25219
- https://lists.debian.org/debian-lts-announce/2021/11/msg00001.html
- https://security.gentoo.org/glsa/202210-25
- https://security.netapp.com/advisory/ntap-20211118-0002/
- https://www.debian.org/security/2021/dsa-4994
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://cert-portal.siemens.com/productcert/pdf/ssa-389290.pdf
