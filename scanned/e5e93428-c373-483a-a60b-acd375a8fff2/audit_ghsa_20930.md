# [H] Dompdf allows remote file inclusion because URI validation failure does not halt font registration

## Summary
Severity: High
Advisory: GHSA-6x28-7h8c-chx4
CVE: CVE-2022-41343
CWE: CWE-552
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-09-26
Source: https://github.com/advisories/GHSA-6x28-7h8c-chx4
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0 <2.0.1

## Details
`registerFont` in `FontMetrics.php` in Dompdf before 2.0.1 allows remote file inclusion because a URI validation failure does not halt font registration, as demonstrated by a `@font-face` rule.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-41343
- https://github.com/dompdf/dompdf/issues/2994
- https://github.com/dompdf/dompdf/pull/2995
- https://github.com/dompdf/dompdf/commit/66431c58017d5b1bdb9f6f772b9fbbc5e3d38dc2
- https://github.com/FriendsOfPHP/security-advisories/blob/master/dompdf/dompdf/CVE-2022-41343.yaml
- https://github.com/advisories/GHSA-6x28-7h8c-chx4
- https://github.com/dompdf/dompdf
- https://github.com/dompdf/dompdf/releases/tag/v2.0.1
- https://tantosec.com/blog/cve-2022-41343
