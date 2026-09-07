# [M] Cross-Site Scripting in ternary conditional operator

## Summary
Severity: Medium
Advisory: GHSA-7733-hjv6-4h47
CVE: CVE-2020-15241
CWE: CWE-601, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-10-08
Source: https://github.com/advisories/GHSA-7733-hjv6-4h47
Type: github-advisory

## Affected
- Packagist: `typo3fluid/fluid` — affected >=2.0.0 <2.0.5
- Packagist: `typo3fluid/fluid` — affected >=2.1.0 <2.1.4
- Packagist: `typo3fluid/fluid` — affected >=2.2.0 <2.2.1
- Packagist: `typo3fluid/fluid` — affected >=2.3.0 <2.3.5
- Packagist: `typo3fluid/fluid` — affected >=2.4.0 <2.4.1
- Packagist: `typo3fluid/fluid` — affected >=2.5.0 <2.5.5
- Packagist: `typo3fluid/fluid` — affected >=2.6.0 <2.6.1
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.25
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.6
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.25
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.6

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:N/E:F/RL:O/RC:C`(5.0)
> * CWE-79

---

:information_source: &nbsp;This vulnerability has been fixed in May 2019 already, CVE and GHSA were assigned later in October 2020

---

### Problem
It has been discovered that the Fluid Engine (package `typo3fluid/fluid`) is vulnerable to cross-site scripting when making use of the ternary conditional operator in templates like the following.

```
{showFullName ? fullName : defaultValue}
```

### Solution
Update to versions 2.0.5, 2.1.4, 2.2.1, 2.3.5, 2.4.1, 2.5.5 or 2.6.1 of this `typo3fluid/fluid` package that fix the problem described.

Updated versions of this package are bundled in following TYPO3 (`typo3/cms-core`) releases:
* TYPO3 v8.7.25 (using `typo3fluid/fluid` v2.5.5)
* TYPO3 v9.5.6 (using `typo3fluid/fluid` v2.6.1)

### Credits
Thanks to Bill Dagou who reported this issue and to TYPO3 core merger Claus Due who fixed the issue.

### References
* [TYPO3-CORE-SA-2019-013](https://typo3.org/security/advisory/typo3-core-sa-2019-013)

## References
- https://github.com/TYPO3/Fluid/security/advisories/GHSA-7733-hjv6-4h47
- https://nvd.nist.gov/vuln/detail/CVE-2020-15241
- https://github.com/TYPO3/Fluid/commit/9ef6a8ffff2e812025fc0701b4ce72eea6911a3d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2020-15241.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2020-15241.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3fluid/fluid/CVE-2020-15241.yaml
- https://github.com/TYPO3/Fluid
- https://typo3.org/security/advisory/typo3-core-sa-2019-013
