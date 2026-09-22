# [M] Cross-Site Request Forgery allowing sending of test emails and generation of node auto-deployment keys

## Summary
Severity: Medium
Advisory: GHSA-wwgq-9jhf-qgw6
CVE: CVE-2021-41273
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-11-18
Source: https://github.com/advisories/GHSA-wwgq-9jhf-qgw6
Type: github-advisory

## Affected
- Packagist: `pterodactyl/panel` — affected >=0 <1.6.6

## Details
### Impact
Due to improperly configured CSRF protections on two routes, a malicious user could execute a CSRF-based attack against the following endpoints:

* Sending a test email.
* Generating a node auto-deployment token.

At no point would any data be exposed to the malicious user, this would simply trigger email spam to an administrative user, or generate a single auto-deployment token unexpectedly. This token is not revealed to the malicious user, it is simply created unexpectedly in the system.

### Patches
This has been addressed in https://github.com/pterodactyl/panel/commit/bf9cbe2c6d5266c6914223e067c56175de7fc3a5 which will be released as `1.6.6`.

### Workarounds
Users may optionally manually apply the fixes released in v1.6.6 to patch their own systems.

## References
- https://github.com/pterodactyl/panel/security/advisories/GHSA-wwgq-9jhf-qgw6
- https://nvd.nist.gov/vuln/detail/CVE-2021-41273
- https://github.com/pterodactyl/panel/commit/bf9cbe2c6d5266c6914223e067c56175de7fc3a5
- https://github.com/pterodactyl/panel
