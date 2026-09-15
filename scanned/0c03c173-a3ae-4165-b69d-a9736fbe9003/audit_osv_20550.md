# [M] CVE-2021-3504

## Summary
Severity: Medium
Advisory: CVE-2021-3504
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:L)
Published: 2021-05-11
Source: https://osv.dev/vulnerability/CVE-2021-3504
Type: osv

## Details
A flaw was found in the hivex library in versions before 1.3.20. It is caused due to a lack of bounds check within the hivex_open function. An attacker could input a specially crafted Windows Registry (hive) file which would cause hivex to read memory beyond its normal bounds or cause the program to crash. The highest threat from this vulnerability is to system availability.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/A5BNKNVYFL36P2GBEB5O36LHFRYU575H/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/BQXTEACRWYAZVNEOIWIYUFGG4GOXSQ22/
- https://lists.debian.org/debian-lts-announce/2021/05/msg00011.html
- https://bugzilla.redhat.com/show_bug.cgi?id=1949687
