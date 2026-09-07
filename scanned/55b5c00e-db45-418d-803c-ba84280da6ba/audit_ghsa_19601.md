# [M] Silverstripe Framework has a XSS vulnerability in HTML editor

## Summary
Severity: Medium
Advisory: GHSA-rhx4-hvx9-j387
CVE: CVE-2025-30148
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2025-04-10
Source: https://github.com/advisories/GHSA-rhx4-hvx9-j387
Type: github-advisory

## Affected
- Packagist: `silverstripe/framework` — affected >=0 <5.3.23

## Details
### Impact

A bad actor with access to edit content in the CMS could send a specifically crafted encoded payload to the server, which could be used to inject a JavaScript payload on the front end of the site. The payload would be sanitised on the client-side, but server-side sanitisation doesn't catch it.

The server-side sanitisation logic has been updated to sanitise against this attack.

### Reported by

James Nicoll from Fujitsu Cyber

### References

- https://www.silverstripe.org/download/security-releases/cve-2025-30148

## References
- https://github.com/silverstripe/silverstripe-framework/security/advisories/GHSA-rhx4-hvx9-j387
- https://nvd.nist.gov/vuln/detail/CVE-2025-30148
- https://github.com/silverstripe/silverstripe-framework/pull/11682
- https://github.com/silverstripe/silverstripe-framework/commit/e99cfd62d160d145a76fcf9631e6b11226e42358
- https://github.com/FriendsOfPHP/security-advisories/blob/master/silverstripe/framework/CVE-2025-30148.yaml
- https://github.com/silverstripe/silverstripe-framework
- https://www.silverstripe.org/download/security-releases/cve-2025-30148
