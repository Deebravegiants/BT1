# [M] Prevent XSS from Confidant API call

## Summary
Severity: Medium
Advisory: GHSA-rxq8-q85f-m866
CVE: CVE-2024-45793
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-09-20
Source: https://github.com/advisories/GHSA-rxq8-q85f-m866
Type: github-advisory

## Affected
- PyPI: `confidant` — affected >=0 <6.6.2

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
Potential XSS from API calls below:
GET <app>/v1/credentials
GET <app>/v1/credentials/<id>
GET <app>/v1/archive/credentials/<id>
GET <app>/v1/archive/credentials
POST <app>/v1/credentials
PUT <app>/v1/credentials/<id>
PUT <app>/v1/credentials/<id>/<to_revision>

GET <app>/v1/services
GET <app>/v1/services/<id>
GET <app>/v1/archive/services/<id>
GET <app>/v1/archive/services
PUT <app>/v1/services/<id>
PUT <app>/v1/services/<id>/<to_revision>

Stored XSS that can only be used as a stored HTML injection. The attacker needs to be authenticated and have privileges to create new credentials, but could use this to show information and run scripts to other users into the same Confidant instance.

### Patches
_Has the problem been patched? What versions should users upgrade to?_
yes, version 6.6.2

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
NO

### References
_Are there any links users can visit to find out more?_
https://hackerone.com/reports/2332004
https://hackerone.com/reports/2456673
https://hackerone.com/reports/2476542
Acknowledgement: 
Thank you Rein Daelman ([trein](https://hackerone.com/trein)) for reporting and proposing the fix.

## References
- https://github.com/lyft/confidant/security/advisories/GHSA-rxq8-q85f-m866
- https://nvd.nist.gov/vuln/detail/CVE-2024-45793
- https://github.com/lyft/confidant/commit/8876b07abde0c8d2a4974f79b60562b6d0193db9
- https://hackerone.com/reports/2332004
- https://hackerone.com/reports/2456673
- https://hackerone.com/reports/2476542
- https://github.com/lyft/confidant
