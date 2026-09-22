# [C] MISP:  Improper access control in auth key reset allows privilege escalation to site administrator

## Summary
Severity: Critical
Advisory: CVE-2026-44380
Aliases: GHSA-3939-4g6m-m3hc
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44380
Type: osv

## Details
MISP is an open source threat intelligence and sharing platform. Prior to 2.5.37, an improper access control vulnerability in the authentication key reset functionality allowed an authenticated organization administrator to reset authentication keys belonging to site administrator accounts within the same organization. Because non-site administrators were not explicitly prevented from accessing or resetting site administrator auth keys, an attacker with organization administrator privileges could potentially obtain a newly generated auth key for a higher-privileged account and use it to escalate privileges. This vulnerability is fixed in 2.5.37.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44380.json
- https://github.com/MISP/MISP/security/advisories/GHSA-3939-4g6m-m3hc
- https://nvd.nist.gov/vuln/detail/CVE-2026-44380
