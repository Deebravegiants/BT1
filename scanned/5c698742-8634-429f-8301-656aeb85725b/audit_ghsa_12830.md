# [M] Barzahlen Payment Module PHP SDK vulnerable to Observable Timing Discrepancy

## Summary
Severity: Medium
Advisory: GHSA-vg5x-6q66-rvgx
CVE: CVE-2016-15015
CWE: CWE-203, CWE-208
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-01-08
Source: https://github.com/advisories/GHSA-vg5x-6q66-rvgx
Type: github-advisory

## Affected
- Packagist: `barzahlen/barzahlen-php` — affected >=0 <2.0.1

## Details
A vulnerability, which was classified as problematic, was found in viafintech Barzahlen Payment Module PHP SDK up to 2.0.0. Affected is the function `verify` of the file `src/Webhook.php`. The manipulation leads to observable timing discrepancy. Upgrading to version 2.0.1 is able to address this issue. The name of the patch is 3e7d29dc0ca6c054a6d6e211f32dae89078594c1. It is recommended to upgrade the affected component. VDB-217650 is the identifier assigned to this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-15015
- https://github.com/viafintech/Barzahlen-PHP/pull/8
- https://github.com/viafintech/Barzahlen-PHP/commit/3e7d29dc0ca6c054a6d6e211f32dae89078594c1
- https://github.com/viafintech/Barzahlen-PHP
- https://github.com/viafintech/Barzahlen-PHP/releases/tag/v2.0.1
- https://vuldb.com/?ctiid.217650
- https://vuldb.com/?id.217650
