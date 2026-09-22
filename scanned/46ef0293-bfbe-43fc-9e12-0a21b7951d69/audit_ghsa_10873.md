# [C] MantisBT is vulnerable to authentication bypass through the SOAP API on MySQL

## Summary
Severity: Critical
Advisory: GHSA-phrq-pc6r-f6gh
CVE: CVE-2026-30849
CWE: CWE-305
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-03-23
Source: https://github.com/advisories/GHSA-phrq-pc6r-f6gh
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.28.1

## Details
Mantis Bug Tracker instances running on MySQL and compatible databases are affected by an authentication bypass vulnerability in the SOAP API, as a result of improper type checking on the password parameter.

Other database backends are not affected, as they do not perform implicit type conversion from string to integer.

### Impact
Using a crafted SOAP envelope, an attacker knowing the victim's username is able to login to the SOAP API with their account without knowledge of the actual password, and execute any API function they have access to.

### Patches
* b349e5c890eeda9bd82e7c7e14479853f8a30d9f

### Workarounds
- [Disabling the SOAP API](https://mantisbt.org/docs/master/en-US/Admin_Guide/html-desktop/#admin.config.api.disable) significantly reduces the risk, but still allows the attacker to retrieve user account information including email address and real name.

### Resources
- https://mantisbt.org/bugs/view.php?id=36902

### Credits
MantisBT thanks Alexander Philiotis of SynerComm for discovering and responsibly reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-phrq-pc6r-f6gh
- https://nvd.nist.gov/vuln/detail/CVE-2026-30849
- https://github.com/mantisbt/mantisbt/commit/b349e5c890eeda9bd82e7c7e14479853f8a30d9f
- https://github.com/mantisbt/mantisbt
