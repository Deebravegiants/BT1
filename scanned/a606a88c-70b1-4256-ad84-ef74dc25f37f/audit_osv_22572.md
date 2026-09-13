# [M] ovs - buffer over-read

## Summary
Severity: Medium
Advisory: CVE-2022-32166
CVSS: 6.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:H)
Published: 2022-09-28
Source: https://osv.dev/vulnerability/CVE-2022-32166
Type: osv

## Details
In ovs versions v0.90.0 through v2.5.0 are vulnerable to heap buffer over-read in flow.c. An unsafe comparison of “minimasks” function could lead access to an unmapped region of memory. This vulnerability is capable of crashing the software, memory modification, and possible remote execution.

## References
- https://www.mend.io/vulnerability-database/CVE-2022-32166
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/32xxx/CVE-2022-32166.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-32166
- https://github.com/cloudbase/ovs/commit/2ed6505555cdcb46f9b1f0329d1491b75290fc73
- https://lists.debian.org/debian-lts-announce/2022/10/msg00036.html
