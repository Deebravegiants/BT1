# [M] CVE-2026-71190

## Summary
Severity: Medium
Advisory: CVE-2026-71190
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-71190
Type: osv

## Details
In OpenStack Swift through 2.38.0, the proxy server Accept header parser contains a regular expression vulnerable to catastrophic backtracking (ReDoS). The "qdtext" pattern (?:[^"]|\\.)* allows an unauthenticated remote attacker to send a crafted Accept header that causes exponential CPU consumption in the proxy worker. A payload of 32 backslash-character pairs exceeds 30 seconds of CPU time. No authentication is required. Repeated requests can exhaust all proxy worker threads, resulting in a complete denial of service.

## References
- http://www.openwall.com/lists/oss-security/2026/08/05/19
- https://opendev.org/openstack/swift
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/71xxx/CVE-2026-71190.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-71190
- https://openwall.com/lists/oss-security/2026/07/28/27
- https://security.openstack.org/ossa/OSSA-2026-031.html
- https://launchpad.net/bugs/2158771
