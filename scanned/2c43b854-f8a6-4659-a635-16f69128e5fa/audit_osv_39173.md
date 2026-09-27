# [M] Warpgate: SSO CSRF -- State Token Not Validated on Return

## Summary
Severity: Medium
Advisory: CVE-2026-44347
Aliases: GHSA-rj86-hm3r-c275
CVSS: 5.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:N/I:H/A:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44347
Type: osv

## Details
Warpgate is an open source SSH, HTTPS and MySQL bastion host for Linux. Prior to 0.23.3, the SSO flow does not validate the state parameter, which makes it possible for an attacker to trick a user into logging into the attacker's account, possibly convincing them to perform sensitive actions on the attacker's account (such as writing sensitive data to the attacker's SSH target, or logging into an HTTP target that the attacker set up). This vulnerability is fixed in 0.23.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44347.json
- https://github.com/warp-tech/warpgate/security/advisories/GHSA-rj86-hm3r-c275
- https://nvd.nist.gov/vuln/detail/CVE-2026-44347
