# [M] yiisoft Yii2 Deserialization of Untrusted Data

## Summary
Severity: Medium
Advisory: GHSA-88m2-j94x-v4fx
CVE: CVE-2025-2689
CWE: CWE-20, CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-03-24
Source: https://github.com/advisories/GHSA-88m2-j94x-v4fx
Type: github-advisory

## Affected
- Packagist: `yiisoft/yii2-dev` — affected >=0

## Details
A vulnerability, which was classified as critical, has been found in yiisoft Yii2 up to 2.0.45. Affected by this issue is the function getIterator of the file symfony\finder\Iterator\SortableIterator.php. The manipulation leads to deserialization. The attack may be launched remotely. The exploit has been disclosed to the public and may be used.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-2689
- https://github.com/gaorenyusi/gaorenyusi/blob/main/Yii2.md
- https://github.com/yiisoft/yii2
- https://vuldb.com/?ctiid.300710
- https://vuldb.com/?id.300710
- https://vuldb.com/?submit.521709
