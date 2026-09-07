# [H] dset Prototype Pollution vulnerability

## Summary
Severity: High
Advisory: GHSA-f6v4-cf5j-vf3w
CVE: CVE-2024-21529
CWE: CWE-1321
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2024-09-11
Source: https://github.com/advisories/GHSA-f6v4-cf5j-vf3w
Type: github-advisory

## Affected
- npm: `dset` — affected >=0 <3.1.4

## Details
Versions of the package dset before 3.1.4 are vulnerable to Prototype Pollution via the dset function due improper user input sanitization. This vulnerability allows the attacker to inject malicious object property using the built-in Object property __proto__, which is recursively assigned to all the objects in the program.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-21529
- https://github.com/lukeed/dset/commit/16d6154e085bef01e99f01330e5a421a7f098afa
- https://github.com/lukeed/dset
- https://security.snyk.io/vuln/SNYK-JS-DSET-7116691
