# [M] Mautic has an Open Redirect vulnerability on user unlock path.

## Summary
Severity: Medium
Advisory: GHSA-6vx9-9r2g-8373
CVE: CVE-2025-5256
CWE: CWE-601
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-05-28
Source: https://github.com/advisories/GHSA-6vx9-9r2g-8373
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=1.0.0 <4.4.16
- Packagist: `mautic/core` — affected >=5.0.0-alpha <5.2.6
- Packagist: `mautic/core` — affected >=6.0.0-alpha <6.0.2

## Details
### Summary
This advisory addresses an Open Redirection vulnerability in Mautic's user unlocking endpoint. This vulnerability could be exploited by an attacker to redirect legitimate users to malicious websites, potentially leading to phishing attacks or the delivery of exploit kits.

Open Redirection via `returnUrl` Parameter: An Open Redirection vulnerability exists in the `/s/action/unlock/user.user/0` endpoint. The `returnUrl` parameter, intended for post-action redirection, is not properly validated. This allows an attacker to craft a URL that, when clicked by a user, redirects them to an arbitrary external website controlled by the attacker.

### Mitigation
Update Mautic to a version that properly validates or sanitizes the `returnUrl` parameter to ensure that redirects only occur to trusted, internal URLs or explicitly whitelisted domains.

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-6vx9-9r2g-8373
- https://nvd.nist.gov/vuln/detail/CVE-2025-5256
- https://github.com/mautic/mautic
