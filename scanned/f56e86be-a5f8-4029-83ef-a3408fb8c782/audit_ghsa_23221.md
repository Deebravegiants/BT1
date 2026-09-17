# [M] DOMPDF Arbitrary File Read

## Summary
Severity: Medium
Advisory: GHSA-qr6q-w4gj-3865
CVE: CVE-2014-2383
CWE: CWE-200
Ecosystem: Packagist
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-qr6q-w4gj-3865
Type: github-advisory

## Affected
- Packagist: `dompdf/dompdf` — affected >=0.6.0 <0.6.1

## Details
dompdf.php in dompdf before 0.6.1, when `DOMPDF_ENABLE_PHP` is enabled, allows context-dependent attackers to bypass chroot protections and read arbitrary files via a PHP protocol and wrappers in the input_file parameter, as demonstrated by a `php://filter/read=convert.base64-encode/resource` in the input_file parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-2383
- https://github.com/dompdf/dompdf/commit/23a693993299e669306929e3d49a4a1f7b3fb028
- https://github.com/FriendsOfPHP/security-advisories/blob/master/dompdf/dompdf/CVE-2014-2383.yaml
- https://github.com/dompdf/dompdf
- https://web.archive.org/web/20151215023329/http://www.securityfocus.com/archive/1/531912/100/0/threaded
- http://seclists.org/fulldisclosure/2014/Apr/258
