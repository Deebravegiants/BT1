# [M] phpBB's Smiley Pack acp_icons.php main pack vulnerable to cross site scripting

## Summary
Severity: Medium
Advisory: GHSA-gmx8-8rff-qv6q
CVE: CVE-2023-5917
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:H/UI:R/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2023-11-02
Source: https://github.com/advisories/GHSA-gmx8-8rff-qv6q
Type: github-advisory

## Affected
- Packagist: `phpbb/phpbb` — affected >=0 <3.3.11

## Details
A vulnerability, which was classified as problematic, has been found in phpBB up to 3.3.10. This issue affects the function main of the file `phpBB/includes/acp/acp_icons.php` of the component Smiley Pack Handler. The manipulation of the argument pack leads to cross site scripting. The attack may be initiated remotely. Upgrading to version 3.3.11 is able to address this issue. The patch is named ccf6e6c255d38692d72fcb613b113e6eaa240aac. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-244307.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-5917
- https://github.com/phpbb/phpbb-app/commit/a3a84334f1c17ee57cc9af3d84996af8772736d3
- https://github.com/phpbb/phpbb/commit/ccf6e6c255d38692d72fcb613b113e6eaa240aac
- https://github.com/phpbb/phpbb-app
- https://github.com/phpbb/phpbb/releases/tag/release-3.3.11
- https://vuldb.com/?ctiid.244307
- https://vuldb.com/?id.244307
- https://www.phpbb.com
- https://www.phpbb.com/community/viewtopic.php?t=2646991
