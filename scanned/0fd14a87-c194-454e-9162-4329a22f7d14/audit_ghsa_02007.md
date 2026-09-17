# [C] set-getter Prototype Pollution Vulnerability

## Summary
Severity: Critical
Advisory: GHSA-jv35-xqg7-f92r
CVE: CVE-2021-25949
CWE: CWE-1321, CWE-915
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-06-21
Source: https://github.com/advisories/GHSA-jv35-xqg7-f92r
Type: github-advisory

## Affected
- npm: `set-getter` — affected >=0 <0.1.1

## Details
Prototype pollution vulnerability in ‘set-getter’ version 0.1.0 allows an attacker to cause a denial of service and may lead to remote code execution.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-25949
- https://github.com/doowb/set-getter/commit/66eb3f0d4686a4a8c7c3d6f7ecd8e570b580edc4
- https://github.com/doowb/set-getter
- https://github.com/doowb/set-getter/blob/5bc2750fe1c3db9651d936131be187744111378d/index.js#L56
- https://web.archive.org/web/20210615022308/https://www.whitesourcesoftware.com/vulnerability-database/CVE-2021-25949
