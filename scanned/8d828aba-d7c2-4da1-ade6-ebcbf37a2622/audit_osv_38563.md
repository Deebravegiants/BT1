# [H] blueprintUE: Login Endpoint Has No Rate Limiting, Lockout, or Brute-Force Protection

## Summary
Severity: High
Advisory: CVE-2026-40586
Aliases: GHSA-m6c2-6p3h-8jv2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-04-21
Source: https://osv.dev/vulnerability/CVE-2026-40586
Type: osv

## Details
blueprintUE is a tool to help Unreal Engine developers. Prior to 4.2.0, the login form handler performs no throttling of any kind. Failed authentication attempts are processed at full network speed with no IP-based rate limiting, no per-account attempt counter, no temporary lockout, no progressive delay (Tarpit), and no CAPTCHA challenge. An attacker can submit an unlimited number of credential guesses. The password policy (10+ characters, mixed case, digit, special character) reduces the effective keyspace but does not prevent dictionary attacks, credential stuffing from breached databases, or targeted attacks against known users with predictable passwords. This vulnerability is fixed in 4.2.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/40xxx/CVE-2026-40586.json
- https://github.com/blueprintue/blueprintue-self-hosted-edition/security/advisories/GHSA-m6c2-6p3h-8jv2
- https://nvd.nist.gov/vuln/detail/CVE-2026-40586
