# [M] CVE-2018-8005

## Summary
Severity: Medium
Advisory: CVE-2018-8005
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2018-08-29
Source: https://osv.dev/vulnerability/CVE-2018-8005
Type: osv

## Details
When there are multiple ranges in a range request, Apache Traffic Server (ATS) will read the entire object from cache. This can cause performance problems with large objects in cache. This affects versions 6.0.0 to 6.2.2 and 7.0.0 to 7.1.3. To resolve this issue users running 6.x users should upgrade to 6.2.3 or later versions and 7.x users should upgrade to 7.1.4 or later versions.

## References
- https://lists.apache.org/thread.html/55d225af92887bfed0194400fd1b718622cca4140fc7318d982e25ca%40%3Cusers.trafficserver.apache.org%3E
- http://www.securityfocus.com/bid/105187
- https://github.com/apache/trafficserver/pull/3106
- https://github.com/apache/trafficserver/pull/3124
- https://www.debian.org/security/2018/dsa-4282
