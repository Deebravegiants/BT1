# [M] Unrestricted Upload of File with Dangerous Type in yetiforce-crm

## Summary
Severity: Medium
Advisory: GHSA-pqr6-3j58-9w58
CVE: CVE-2022-1411
CWE: CWE-434
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-06
Source: https://github.com/advisories/GHSA-pqr6-3j58-9w58
Type: github-advisory

## Affected
- Packagist: `yetiforce/yetiforce-crm` — affected >=0 <6.4.0

## Details
Unrestructed file upload in GitHub repository yetiforcecompany/yetiforcecrm prior to 6.4.0. Attacker can send malicious files to the victims is able to retrieve the stored data from the web application without that data being made safe to render in the browser and steals victim's cookie leads to account takeover.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-1411
- https://github.com/yetiforcecompany/yetiforcecrm/commit/bf69c427260011ffca42f7b6935bb54080c54124
- https://github.com/yetiforcecompany/yetiforcecrm
- https://huntr.dev/bounties/75c7cf09-d118-4f91-9686-22b142772529
