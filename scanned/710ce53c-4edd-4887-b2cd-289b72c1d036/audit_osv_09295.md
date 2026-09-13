# [C] CVE-2016-9427

## Summary
Severity: Critical
Advisory: CVE-2016-9427
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-12-12
Source: https://osv.dev/vulnerability/CVE-2016-9427
Type: osv

## Details
Integer overflow vulnerability in bdwgc before 2016-09-27 allows attackers to cause client of bdwgc denial of service (heap buffer overflow crash) and possibly execute arbitrary code via huge allocation.

## References
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00089.html
- http://lists.opensuse.org/opensuse-updates/2016-12/msg00115.html
- http://www.openwall.com/lists/oss-security/2016/11/18/3
- http://www.securityfocus.com/bid/94407
- https://lists.debian.org/debian-lts-announce/2022/03/msg00039.html
- https://github.com/ivmai/bdwgc/issues/135
