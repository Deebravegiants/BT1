# [H] Logic bug in ajax.render.php allows for bypass of 'backOffice' access control in Combodo iTop

## Summary
Severity: High
Advisory: CVE-2024-51995
Aliases: GHSA-3mxr-8r3j-j2j9
CVSS: 7.1 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N)
Published: 2024-11-07
Source: https://osv.dev/vulnerability/CVE-2024-51995
Type: osv

## Details
Combodo iTop is a web based IT Service Management tool. An attacker can request any `route` we want as long as we specify an `operation` that is allowed. This issue has been addressed in version 3.2.0 by applying the same access control pattern as in `UI.php` to the `ajax.render.php` page which does not allow arbitrary `routes` to be dispatched. All users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/51xxx/CVE-2024-51995.json
- https://github.com/Combodo/iTop/security/advisories/GHSA-3mxr-8r3j-j2j9
- https://nvd.nist.gov/vuln/detail/CVE-2024-51995
