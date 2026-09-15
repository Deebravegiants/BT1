# [M] CVE-2015-8792

## Summary
Severity: Medium
Advisory: CVE-2015-8792
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2016-01-29
Source: https://osv.dev/vulnerability/CVE-2015-8792
Type: osv

## Details
The KaxInternalBlock::ReadData function in libMatroska before 1.4.4 allows context-dependent attackers to obtain sensitive information from process heap memory via crafted EBML lacing, which triggers an invalid memory access.

## References
- http://www.debian.org/security/2016/dsa-3526
- http://lists.matroska.org/pipermail/matroska-users/2015-October/006985.html
- https://github.com/Matroska-Org/libmatroska/blob/release-1.4.4/ChangeLog
- https://github.com/Matroska-Org/libmatroska/commit/0a2d3e3644a7453b6513db2f9bc270f77943573f
- http://lists.opensuse.org/opensuse-updates/2016-01/msg00035.html
