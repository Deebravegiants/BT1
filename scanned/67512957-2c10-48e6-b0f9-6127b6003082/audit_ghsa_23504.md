# [M] Moodle directory traversal vulnerability

## Summary
Severity: Medium
Advisory: GHSA-gphj-63h8-r9vq
CVE: CVE-2015-1493
CWE: CWE-22
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-gphj-63h8-r9vq
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=0 <2.6.8
- Packagist: `moodle/moodle` — affected >=2.7.0 <2.7.5
- Packagist: `moodle/moodle` — affected >=2.8.0 <2.8.3

## Details
Directory traversal vulnerability in the min_get_slash_argument function in lib/configonlylib.php in Moodle through 2.5.9, 2.6.x before 2.6.8, 2.7.x before 2.7.5, and 2.8.x before 2.8.3 allows remote authenticated users to read arbitrary files via a .. (dot dot) in the file parameter, as demonstrated by reading PHP scripts.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-1493
- https://github.com/moodle/moodle/commit/0289be1321babfa588fb5b18ebb08a296eed9eee
- https://github.com/moodle/moodle/commit/a72f2cca7f08c354c18a3923c3f05eee50bdd434
- https://github.com/moodle/moodle/commit/af9a7937cc085f96bdbc4724cadec6eeae0242fc
- https://github.com/moodle/moodle/commit/cc496f5b27d36a8df4bcede997a484eb9719363b
- https://github.com/moodle/moodle
- https://moodle.org/mod/forum/discuss.php?d=279956
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-48980
- http://git.moodle.org/gw?p=moodle.git;a=commit;h=af9a7937cc085f96bdbc4724cadec6eeae0242fc
- http://openwall.com/lists/oss-security/2015/02/04/15
- http://openwall.com/lists/oss-security/2015/02/09/2
