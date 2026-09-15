# [M] phpSysInfo allows remote attackers to determine the existence of arbitrary files via a .. (dot dot) sequence

## Summary
Severity: Medium
Advisory: GHSA-2wxv-3g4v-p76p
CVE: CVE-2006-3360
CWE: CWE-22
Ecosystem: Packagist
Published: 2022-05-01
Source: https://github.com/advisories/GHSA-2wxv-3g4v-p76p
Type: github-advisory

## Affected
- Packagist: `phpsysinfo/phpsysinfo` — affected >=0 <3.2.5

## Details
Directory traversal vulnerability in index.php in phpSysInfo prior to 3.2.5 allows remote attackers to determine the existence of arbitrary files via a .. (dot dot) sequence and a trailing null (%00) byte in the lng parameter, which will display a different error message if the file exists.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2006-3360
- https://github.com/phpsysinfo/phpsysinfo/issues/107
- https://github.com/phpsysinfo/phpsysinfo/issues/368#issuecomment-1380842745
- https://github.com/phpsysinfo/phpsysinfo/commit/60b5bbb5d1cc17f44050e99a3e746f55a4fd4e18
- https://exchange.xforce.ibmcloud.com/vulnerabilities/27527
- https://github.com/phpsysinfo/phpsysinfo
