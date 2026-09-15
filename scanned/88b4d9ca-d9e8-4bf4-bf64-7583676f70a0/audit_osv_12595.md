# [H] CVE-2018-1318

## Summary
Severity: High
Advisory: CVE-2018-1318
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-08-29
Source: https://osv.dev/vulnerability/CVE-2018-1318
Type: osv

## Details
Adding method ACLs in remap.config can cause a segfault when the user makes a carefully crafted request. This affects versions Apache Traffic Server (ATS) 6.0.0 to 6.2.2 and 7.0.0 to 7.1.3. To resolve this issue users running 6.x should upgrade to 6.2.3 or later versions and 7.x users should upgrade to 7.1.4 or later versions.

## References
- https://lists.apache.org/thread.html/9357cdfb6352f72944411608b712e37196ad9e4bc0f17c4828a26fb2%40%3Cusers.trafficserver.apache.org%3E
- http://www.securityfocus.com/bid/105176
- https://github.com/apache/trafficserver/pull/3195
- https://www.debian.org/security/2018/dsa-4282
