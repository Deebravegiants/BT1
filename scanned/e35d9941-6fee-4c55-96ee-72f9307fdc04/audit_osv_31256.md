# [M] Insecure Account Profile Management

## Summary
Severity: Medium
Advisory: CVE-2024-6895
CVSS: 6.0 (CVSS:4.0/AV:A/AC:H/AT:N/PR:H/UI:P/VC:H/VI:L/VA:L/SC:H/SI:H/SA:H)
Published: 2024-07-19
Source: https://osv.dev/vulnerability/CVE-2024-6895
Type: osv

## Details
Insufficient authentication in user account management in Yugabyte Platform allows local network attackers with a compromised user session to change critical security information without re-authentication. An attacker with user session and access to application can modify settings such as password and email without being prompted for the current password, enabling account takeover.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/6xxx/CVE-2024-6895.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-6895
- https://github.com/yugabyte/yugabyte-db/commit/9687371d8777f876285b737a9d01995bc46bafa5
