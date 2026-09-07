# [H] (ReDoS) Regular Expression Denial of Service in tf2-item-format

## Summary
Severity: High
Advisory: GHSA-8h55-q5qq-p685
CVE: CVE-2024-41655
CWE: CWE-1333, CWE-624
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-07-23
Source: https://github.com/advisories/GHSA-8h55-q5qq-p685
Type: github-advisory

## Affected
- npm: `tf2-item-format` — affected >=4.2.6 <5.9.14

## Details
## Summary

Versions of `tf2-item-format` since at least `4.2.6` are vulnerable to a Regular Expression Denial of Service (ReDoS) attack when parsing crafted user input. 

## Tested Versions

- `5.9.13`
- `5.8.10`
- `5.7.0`
- `5.6.17`
- `4.3.5`
- `4.2.6`

### v5
Upgrade package to `^5.9.14`

### v4
No patch exists. Please consult the [v4 to v5 migration guide](https://github.com/danocmx/node-tf2-item-format?tab=readme-ov-file#migrating-from-v4-to-v5) to upgrade to v5.

If upgrading to v5 is not possible, fork the module repository and implement the fix detailed below.

## Impact

This vulnerability can be exploited by an attacker to perform DoS attacks on any service that uses any `tf2-item-format` to parse user input.

## References
- https://github.com/danocmx/node-tf2-item-format/security/advisories/GHSA-8h55-q5qq-p685
- https://nvd.nist.gov/vuln/detail/CVE-2024-41655
- https://github.com/danocmx/node-tf2-item-format/commit/5cffcc16a9261d6a937bda72bfe6830e02e31eec
- https://github.com/danocmx/node-tf2-item-format
- https://github.com/danocmx/node-tf2-item-format/releases/tag/v5.9.14
