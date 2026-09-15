# [M] CVE-2018-8040

## Summary
Severity: Medium
Advisory: CVE-2018-8040
CVSS: 5.3 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-08-29
Source: https://osv.dev/vulnerability/CVE-2018-8040
Type: osv

## Details
Pages that are rendered using the ESI plugin can have access to the cookie header when the plugin is configured not to allow access. This affects Apache Traffic Server (ATS) versions 6.0.0 to 6.2.2 and 7.0.0 to 7.1.3. To resolve this issue users running 6.x should upgrade to 6.2.3 or later versions and 7.x users should upgrade to 7.1.4 or later versions.

## References
- https://lists.apache.org/thread.html/36b3df68fe7311965f6bc4630ca413d2aa99d8f1d53affda85ea70d7%40%3Cusers.trafficserver.apache.org%3E
- https://lists.apache.org/thread.html/cc7aa2ce1c6f4fe0c6bfef517763cdaad30ec7bcb0115b73f73f3c01%40%3Cusers.trafficserver.apache.org%3E
- http://www.securityfocus.com/bid/105181
- https://www.debian.org/security/2018/dsa-4282
- https://github.com/apache/trafficserver/pull/3926
