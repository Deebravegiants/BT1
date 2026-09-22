# [H] CVE-2016-6171

## Summary
Severity: High
Advisory: CVE-2016-6171
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2017-02-09
Source: https://osv.dev/vulnerability/CVE-2016-6171
Type: osv

## Details
Knot DNS before 2.3.0 allows remote DNS servers to cause a denial of service (memory exhaustion and slave server crash) via a large zone transfer for (1) DDNS, (2) AXFR, or (3) IXFR.

## References
- http://www.openwall.com/lists/oss-security/2016/07/06/3
- http://www.openwall.com/lists/oss-security/2016/07/06/4
- http://www.securityfocus.com/bid/91678
- https://gitlab.labs.nic.cz/labs/knot/blob/c546a70563ef4c7badb7cb5bdf6d1ba8e7adae82/NEWS
- https://gitlab.labs.nic.cz/labs/knot/issues/464
- https://github.com/sischkg/xfer-limit/blob/master/README.md
- https://lists.dns-oarc.net/pipermail/dns-operations/2016-July/015058.html
