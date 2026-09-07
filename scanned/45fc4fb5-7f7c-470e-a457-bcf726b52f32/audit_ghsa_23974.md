# [M] Moodle Authentication Bypass in File Upload

## Summary
Severity: Medium
Advisory: GHSA-w66h-c2vj-cm7f
CVE: CVE-2012-3387
CWE: CWE-287
Ecosystem: Packagist
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-w66h-c2vj-cm7f
Type: github-advisory

## Affected
- Packagist: `moodle/moodle` — affected >=2.3 <2.3.1

## Details
Moodle 2.3.x before 2.3.1 uses only a client-side check for whether references are permitted in a file upload, which allows remote authenticated users to bypass intended alias (aka shortcut) restrictions via a client that omits this check.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2012-3387
- https://github.com/moodle/moodle/commit/3b6629c088f14c6ee8f13a009ff27441d164f334
- https://github.com/moodle/moodle/commit/61a339e59857fd36080f4a468a16cd6a539d90bb
- https://exchange.xforce.ibmcloud.com/vulnerabilities/76954
- https://github.com/moodle/moodle
- https://web.archive.org/web/20121104220059/http://www.securityfocus.com/bid/54481
- http://git.moodle.org/gw?p=moodle.git&a=search&h=HEAD&st=commit&s=MDL-33948
- http://openwall.com/lists/oss-security/2012/07/17/1
