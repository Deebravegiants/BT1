# [M] MantisBT unauthorized disclosure of private project column configuration

## Summary
Severity: Medium
Advisory: GHSA-g582-8vwr-68h2
CVE: CVE-2025-62520
CWE: CWE-285
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-11-03
Source: https://github.com/advisories/GHSA-g582-8vwr-68h2
Type: github-advisory

## Affected
- Packagist: `mantisbt/mantisbt` — affected >=0 <2.27.2

## Details
### Impact

Due to insufficient access-level checks, any non-admin user having access to _manage_config_columns_page.php_ (typically project managers having MANAGER role) can use the _Copy From_ action to retrieve the columns configuration from a private project they have no access to. 

Access to the reverse operation (_Copy To_) is correctly controlled, i.e. it is not possible to alter the private project's configuration.

### Patches
The vulnerability will be fixed in MantisBT version 2.27.2. 

### Workarounds
None

### Credits
Thanks to [d3vpoo1](https://github.com/jrckmcsb) for reporting the issue.

## References
- https://github.com/mantisbt/mantisbt/security/advisories/GHSA-g582-8vwr-68h2
- https://nvd.nist.gov/vuln/detail/CVE-2025-62520
- https://github.com/mantisbt/mantisbt/commit/4fe94f45fa2baea2aeb4b65781d2009e7b4a0bf3
- https://github.com/mantisbt/mantisbt
- https://mantisbt.org/bugs/view.php?id=36502
