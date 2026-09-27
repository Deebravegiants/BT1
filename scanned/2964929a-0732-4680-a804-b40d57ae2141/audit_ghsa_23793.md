# [H] ThinkAdmin directory traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-2qm5-r82g-5hcx
CVE: CVE-2020-25540
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-2qm5-r82g-5hcx
Type: github-advisory

## Affected
- Packagist: `zoujingli/thinkadmin` — affected 6.0

## Details
ThinkAdmin v6 is affected by a directory traversal vulnerability. An unauthorized attacker can read arbitrarily file on a remote server via GET request encode parameter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-25540
- https://github.com/zoujingli/ThinkAdmin/issues/244
- https://github.com/zoujingli/ThinkAdmin/commit/ff2ab47cfabd4784effbf72a2a386c5d25c43a9a
- https://github.com/zoujingli/ThinkAdmin
- https://wtfsec.org/posts/thinkadmin-v6-%E5%88%97%E7%9B%AE%E5%BD%95-%E4%BB%BB%E6%84%8F%E6%96%87%E4%BB%B6%E8%AF%BB%E5%8F%96
- http://packetstormsecurity.com/files/159177/ThinkAdmin-6-Arbitrary-File-Read.html
