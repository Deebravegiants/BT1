# [M] CVE-2026-27855

## Summary
Severity: Medium
Advisory: CVE-2026-27855
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:N)
Published: 2026-03-27
Source: https://osv.dev/vulnerability/CVE-2026-27855
Type: osv

## Details
Dovecot OTP authentication is vulnerable to replay attack under specific conditions. If auth cache is enabled, and username is altered in passdb, then OTP credentials can be cached so that same OTP reply is valid. An attacker able to observe an OTP exchange is able to log in as the user. If authentication happens over unsecure connection, switch to SCRAM protocol. Alternatively ensure the communcations are secured, and if possible switch to OAUTH2 or SCRAM. No publicly available exploits are known.

## References
- https://documentation.open-xchange.com/dovecot/security/advisories/csaf/2026/oxdc-adv-2026-0001.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/27xxx/CVE-2026-27855.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-27855
