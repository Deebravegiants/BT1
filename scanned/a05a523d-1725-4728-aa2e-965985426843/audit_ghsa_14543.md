# [M] Pimcore vulnerable to Cross Site Scripting in Email Blacklist

## Summary
Severity: Medium
Advisory: GHSA-96hp-38wx-j3wc
CVE: CVE-2023-1116
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-03-01
Source: https://github.com/advisories/GHSA-96hp-38wx-j3wc
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.18

## Details
### Impact
The attacker can execute arbitrary JavaScript and steal Cookies information and use them to hijack the user's session.

### Patches
Update to version 10.5.18 or apply this patch manually https://github.com/pimcore/pimcore/pull/14467.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/14467.patch manually.

### References
https://huntr.dev/bounties/3245ff99-9adf-4db9-af94-f995747e09d1/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-96hp-38wx-j3wc
- https://nvd.nist.gov/vuln/detail/CVE-2023-1116
- https://github.com/pimcore/pimcore/pull/14467.patch
- https://github.com/pimcore/pimcore/commit/f6d322efa207a737eedd8726b7c92e957a83341e
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/3245ff99-9adf-4db9-af94-f995747e09d1
