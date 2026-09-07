# [H] CakePHP allows remote attackers to modify internal Cake cache and execute arbitrary code

## Summary
Severity: High
Advisory: GHSA-g2vx-8v47-4vhh
CVE: CVE-2010-4335
CWE: CWE-20
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-g2vx-8v47-4vhh
Type: github-advisory

## Affected
- Packagist: `cakephp/cakephp` — affected >=1.2.8 <1.3.6

## Details
The `_validatePost` function in `libs/controller/components/security.php` in CakePHP 1.3.x through 1.3.5 and 1.2.8 allows remote attackers to modify the internal Cake cache and execute arbitrary code via a crafted `data[_Token][fields]` value that is processed by the unserialize function, as demonstrated by modifying the `file_map` cache to execute arbitrary local files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-4335
- https://github.com/cakephp/cakephp/commit/e431e86aa4301ced4273dc7919b59362cbb353cb
- https://github.com/cakephp/cakephp
- http://malloc.im/CakePHP-unserialize.txt
- http://packetstormsecurity.org/files/view/95847/burnedcake.py.txt
- http://secunia.com/advisories/42211
- http://securityreason.com/securityalert/8026
- http://www.exploit-db.com/exploits/16011
- http://www.osvdb.org/69352
