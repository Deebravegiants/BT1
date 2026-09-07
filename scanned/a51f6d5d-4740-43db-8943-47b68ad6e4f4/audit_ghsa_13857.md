# [C] SQL injection in webbuilders-group silverstripe-kapost-bridge

## Summary
Severity: Critical
Advisory: GHSA-32gr-x76g-267w
CVE: CVE-2015-10077
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-02-10
Source: https://github.com/advisories/GHSA-32gr-x76g-267w
Type: github-advisory

## Affected
- Packagist: `webbuilders-group/silverstripe-kapost-bridge` — affected >=0 <0.4.0

## Details
A vulnerability was found in webbuilders-group silverstripe-kapost-bridge 0.3.3. It has been declared as critical. Affected by this vulnerability is the function index/getPreview of the file code/control/KapostService.php. The manipulation leads to sql injection. The attack can be launched remotely. Upgrading to version 0.4.0 is able to address this issue. The name of the patch is 2e14b0fd0ea35034f90890f364b130fb4645ff35. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-220471.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-10077
- https://github.com/webbuilders-group/silverstripe-kapost-bridge/commit/2e14b0fd0ea35034f90890f364b130fb4645ff35
- https://github.com/webbuilders-group/silverstripe-kapost-bridge
- https://github.com/webbuilders-group/silverstripe-kapost-bridge/releases/tag/0.4.0
- https://vuldb.com/?ctiid.220471
- https://vuldb.com/?id.220471
