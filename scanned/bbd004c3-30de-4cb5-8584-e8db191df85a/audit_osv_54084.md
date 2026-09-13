# [M] CVE-2023-38559

## Summary
Severity: Medium
Advisory: CVE-2023-38559
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-08-01
Source: https://osv.dev/vulnerability/CVE-2023-38559
Type: osv

## Details
A buffer overflow flaw was found in base/gdevdevn.c:1973 in devn_pcx_write_rle() in ghostscript. This issue may allow a local attacker to cause a denial of service via outputting a crafted PDF file for a DEVN device with gs.

## References
- https://lists.debian.org/debian-lts-announce/2023/08/msg00006.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/QH7ERAYSSXEYDWWY7LOV7CA5MIDZN3Z6/
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/GBV6BTUREXM6DB3OGHGLMWGAZ3I45TXE/
- https://access.redhat.com/errata/RHSA-2023:6544
- https://access.redhat.com/errata/RHSA-2023:7053
- https://access.redhat.com/security/cve/CVE-2023-38559
- https://bugs.ghostscript.com/show_bug.cgi?id=706897
- https://bugzilla.redhat.com/show_bug.cgi?id=2224367
- https://git.ghostscript.com/?p=ghostpdl.git;a=commitdiff;h=d81b82c70bc1
