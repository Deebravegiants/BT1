# [M] Silverstripe Framework has a Cross-site Scripting vulnerability with encoded payload

## Summary
Severity: Medium
Advisory: GHSA-chx7-9x8h-r5mg
CVE: CVE-2024-32981
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-17
Source: https://github.com/advisories/GHSA-chx7-9x8h-r5mg
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <5.2.16

## Details
### Impact
A bad actor with access to edit content in the CMS could send a specifically crafted encoded payload to the server, which could be used to inject a JavaScript payload on the front end of the site. The payload would be sanitised on the client-side, but server-side sanitisation doesn't catch it.

The server-side sanitisation logic has been updated to sanitise against this type of attack.

### References
- https://www.silverstripe.org/download/security-releases/cve-2024-32981

## References
- https://github.com/silverstripe/silverstripe-framework/security/advisories/GHSA-chx7-9x8h-r5mg
- https://nvd.nist.gov/vuln/detail/CVE-2024-32981
- https://github.com/silverstripe/silverstripe-framework/commit/b8d20dc9d531550e06fd7da7a0eafa551922e2e1
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2024-32981.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/cve-2024-32981
