# [H] Authentication Bypass in passport-azure-ad

## Summary
Severity: High
Advisory: GHSA-73jp-3c67-hjfv
CVE: CVE-2016-7191
CWE: CWE-287
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-26
Source: https://github.com/advisories/GHSA-73jp-3c67-hjfv
Type: github-advisory

## Affected
- npm: `passport-azure-ad` — affected >=1.0.0 <1.4.6
- npm: `passport-azure-ad` — affected >=2.0.0 <2.0.1

## Details
Affected versions of `passport-azure-ad` do not recognize the `validateIssuer` setting, which allows remote attackers to bypass authentication via a crafted token.


## Recommendation

Version 1.x: Update to version 1.4.6 or later.
Version 2.x: Update to version 2.0.1 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-7191
- https://github.com/AzureAD/passport-azure-ad
- https://github.com/AzureAD/passport-azure-ad/blob/master/SECURITY-NOTICE.MD
- https://github.com/advisories/GHSA-73jp-3c67-hjfv
- https://support.microsoft.com/en-us/kb/3187742
- https://support.microsoft.com/kb/3187742
- https://www.npmjs.com/advisories/151
- http://www.securityfocus.com/bid/93213
- http://www.securitytracker.com/id/1036996
