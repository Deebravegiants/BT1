# [M] Symfony's Cas2Handler Derives CAS service URL from Client Host Header → Cross-Service Ticket Replay

## Summary
Severity: Medium
Advisory: GHSA-j8gj-9rm5-4xhx
CVE: CVE-2026-45074
CWE: CWE-290
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:U (CVSS_V4)
Published: 2026-05-27
Source: https://github.com/advisories/GHSA-j8gj-9rm5-4xhx
Type: github-advisory

## Affected
- Packagist: `symfony/security-http` — affected >=7.1.0 <7.4.12
- Packagist: `symfony/security-http` — affected >=8.0.0 <8.0.12
- Packagist: `symfony/symfony` — affected >=7.1.0 <7.4.12
- Packagist: `symfony/symfony` — affected >=8.0.0 <8.0.12

## Details
`Cas2Handler` builds this `service` parameter from `Request::getSchemeAndHttpHost()`, which reflects the attacker-controlled HTTP `Host` header whenever Symfony's `framework.trusted_hosts` setting is not configured (the default). An attacker who controls any *other* application registered with the same CAS server can replay a victim's ticket against the Symfony application, with a spoofed `Host` header, and be authenticated as that victim.

### Resolution

A new required `service_url` configuration option is introduced on `Cas2Handler`. The CAS `service` parameter sent to the validation endpoint is now built from this configured URL instead of being derived from the request's `Host` header, preventing cross-service ticket replay via Host header spoofing.

The patch for this issue is available [here](https://github.com/symfony/symfony/commit/5ba145dba702404801bdf9e7e8d6df170060d541) for branch 7.4.

### Credits

Symfony would like to thank Claude Mythos Preview (via Project Glasswing) for reporting the issue and Nicolas Grekas for providing the fix.

## References
- https://github.com/symfony/symfony/security/advisories/GHSA-j8gj-9rm5-4xhx
- https://github.com/symfony/symfony/commit/5ba145dba702404801bdf9e7e8d6df170060d541
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/security-http/CVE-2026-45074.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/symfony/symfony/CVE-2026-45074.yaml
- https://github.com/symfony/symfony
- https://symfony.com/cve-2026-45074
