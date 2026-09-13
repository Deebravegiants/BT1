# [M] Wazuh: API brute-force protection bypass via race condition in login attempt tracking

## Summary
Severity: Medium
Advisory: CVE-2026-26206
Aliases: GHSA-m2mr-xhhv-jx58
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2026-04-29
Source: https://osv.dev/vulnerability/CVE-2026-26206
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From version 4.0.0 to before version 4.14.4, Wazuh's server API brute-force protection for POST /security/user/authenticate can be bypassed by sending concurrent authentication requests. Although the configured threshold (max_login_attempts, default 50) is enforced correctly for sequential requests, a parallel burst allows significantly more failed login attempts to be processed before the IP block is applied. This enables an attacker to perform more password guesses than the configured policy intends (e.g., 100 attempts processed where 50 should be allowed). This issue has been patched in version 4.14.4.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.4
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26206.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-m2mr-xhhv-jx58
- https://nvd.nist.gov/vuln/detail/CVE-2026-26206
