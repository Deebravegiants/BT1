# [M] OPNsense: Authentication lockout bypass

## Summary
Severity: Medium
Advisory: CVE-2026-44195
Aliases: GHSA-h3vx-4q27-rc42
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2026-05-13
Source: https://osv.dev/vulnerability/CVE-2026-44195
Type: osv

## Details
OPNsense is a FreeBSD based firewall and routing platform. Prior to 26.1.7, a logic flaw in the OPNsense lockout_handler allows an unauthenticated attacker to continuously reset the authentication failure counter for their IP address. By interjecting a crafted username containing a success keyword ("Accepted" or "Successful login") between normal brute-force attempts, an attacker can prevent the failure counter from ever reaching the lockout threshold. This vulnerability is fixed in 26.1.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44195.json
- https://github.com/opnsense/core/security/advisories/GHSA-h3vx-4q27-rc42
- https://nvd.nist.gov/vuln/detail/CVE-2026-44195
- https://gist.github.com/sopex/b9786e72e2a5d9b1bbd81ed8477c351b
