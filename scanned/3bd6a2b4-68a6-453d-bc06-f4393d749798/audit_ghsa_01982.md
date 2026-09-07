# [C] Deserialization of Untrusted Data in NukeViet

## Summary
Severity: Critical
Advisory: GHSA-32wr-8wxm-852c
CVE: CVE-2019-7725
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-22
Source: https://github.com/advisories/GHSA-32wr-8wxm-852c
Type: github-advisory

## Affected
- Packagist: `nukeviet/nukeviet` — affected >=0 <4.3.04

## Details
includes/core/is_user.php in NukeViet before 4.3.04 deserializes the untrusted nvloginhash cookie (i.e., the code relies on PHP's serialization format when JSON can be used to eliminate the risk).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-7725
- https://github.com/nukeviet/nukeviet/pull/2740/commits/05dfb9b4531f12944fe39556f58449b9a56241be
- https://github.com/nukeviet/nukeviet/blob/4.3.04/CHANGELOG.txt
- https://github.com/nukeviet/nukeviet/blob/nukeviet4.3/CHANGELOG.txt
- https://github.com/nukeviet/nukeviet/compare/4.3.03...4.3.04
