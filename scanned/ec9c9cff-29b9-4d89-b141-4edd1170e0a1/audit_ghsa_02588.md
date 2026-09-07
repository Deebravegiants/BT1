# [H] Stored XSS vulnerability on Bounce Management Callback

## Summary
Severity: High
Advisory: GHSA-86pv-95mj-7w5f
CVE: CVE-2021-27910
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2021-09-01
Source: https://github.com/advisories/GHSA-86pv-95mj-7w5f
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=0 <3.3.4
- Packagist: `mautic/core` — affected >=4.0.0-alpha1 <4.0.0

## Details
### Impact
Insufficient sanitization / filtering allows for arbitrary JavaScript Injection in Mautic using the bounce management callback function. The values submitted in the "error" and "error_related_to" parameters of the POST request of the bounce management callback will be permanently stored and executed once the details page of an affected lead is opened by a Mautic user.

An attacker with access to the bounce management callback function (identified with the Mailjet webhook, but it is assumed this will work uniformly across all kinds of webhooks) can inject arbitrary JavaScript Code into the "error" and "error_related_to" parameters of the POST request (POST /mailer/<product / webhook>/callback). It is noted that there is no authentication needed to access this function.

The JavaScript Code is stored permanently in the web application and executed every time an authenticated user views the details page of a single contact / lead in Mautic. This means, arbitrary code can be executed to, e.g., steal or tamper with information.

### Patches
Upgrade to 3.3.4 or 4.0.0

### Workarounds
No

### References
https://github.com/mautic/mautic/releases/tag/3.3.4
https://github.com/mautic/mautic/releases/tag/4.0.0

### For more information
If you have any questions or comments about this advisory:

* Email us at [security@mautic.org](mailto:security@mautic.org)

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-86pv-95mj-7w5f
- https://nvd.nist.gov/vuln/detail/CVE-2021-27910
- https://github.com/mautic/mautic/commit/e6a405975342f3cf86aa71927618d31d25135fa3
- https://github.com/FriendsOfPHP/security-advisories/blob/master/mautic/core/CVE-2021-27910.yaml
- https://github.com/mautic/mautic
