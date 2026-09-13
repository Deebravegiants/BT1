# [M] Wazuh: Username Enumeration via Timing Side-Channel

## Summary
Severity: Medium
Advisory: CVE-2026-44255
Aliases: GHSA-3978-44q9-9px9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-44255
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. From 4.0.0 until 4.14.6 and 5.0.0-beta2, AuthenticationManager.check_user() in framework/wazuh/rbac/orm.py performs check_password_hash() only when the supplied username exists. A nonexistent username returns immediately, while a valid username causes an expensive bcrypt calculation. An unauthenticated remote attacker can compare authentication response times to enumerate valid Wazuh usernames and use that information in subsequent credential attacks. This issue is fixed in versions 4.14.6 and 5.0.0-beta2.

## References
- https://github.com/wazuh/wazuh/releases/tag/v4.14.6
- https://github.com/wazuh/wazuh/releases/tag/v5.0.0-beta2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44255.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-3978-44q9-9px9
- https://nvd.nist.gov/vuln/detail/CVE-2026-44255
- https://github.com/wazuh/wazuh/commit/5ecea7b38b998407cb0d205467dd247140a0f981
- https://github.com/wazuh/wazuh/pull/35757
