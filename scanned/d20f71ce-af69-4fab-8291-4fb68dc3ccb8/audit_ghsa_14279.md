# [H] HTML injection in search results via plaintext message highlighting

## Summary
Severity: High
Advisory: GHSA-xv83-x443-7rmw
CVE: CVE-2023-30609
CWE: CWE-74, CWE-79
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:L (CVSS_V3)
Published: 2023-04-25
Source: https://github.com/advisories/GHSA-xv83-x443-7rmw
Type: github-advisory

## Affected
- npm: `matrix-react-sdk` — affected >=0 <3.71.0

## Details
### Impact
Plain text messages containing HTML tags are rendered as HTML in the search results. To exploit this, an attacker needs to trick a user into searching for a specific message containing an HTML injection payload.

Cross-site scripting is possible by including resources from `recaptcha.net` and `gstatic.com` which are included in the default CSP.

Thanks to [Cadence Ember](https://cadence.moe/) for finding the injection and to [S1m](https://github.com/p1gp1g/) for finding possible XSS vectors.

### Patches
Version 3.71.0 of the SDK fixes the issue.

### Workarounds
Restarting the client will clear the injection.

## References
- https://github.com/matrix-org/matrix-react-sdk/security/advisories/GHSA-xv83-x443-7rmw
- https://nvd.nist.gov/vuln/detail/CVE-2023-30609
- https://github.com/matrix-org/matrix-react-sdk/commit/bf182bc94556849d7acdfa0e5fdea2aa129ea826
- https://github.com/matrix-org/matrix-react-sdk
- https://github.com/matrix-org/matrix-react-sdk/releases/tag/v3.71.0
