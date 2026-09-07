# [M] pimcore is vulnerable to cross-site scripting via "title field " in data objects

## Summary
Severity: Medium
Advisory: GHSA-6vf6-g3pr-j83h
CVE: CVE-2023-0323
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-01-20
Source: https://github.com/advisories/GHSA-6vf6-g3pr-j83h
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.14

## Details
### Impact
The vulnerability is capable of resulting in stolen user cookies.

#### Proof of Concept
```
Login with dev account https://11.x-dev.pimcore.fun/admin/?_dc=1670962076&perspective=

Go to setting --> data objects --> classes --> events

Click media under genaral settings

Add payload in title field.

Go to data objects module and open events, xss will trigger

// PoC.js "><iMg SrC="x" oNeRRor="alert(xss);">
```
### Patches
Update to version 10.5.14 or apply this patch manually https://github.com/pimcore/pimcore/pull/13916.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/13916.patch manually.

### References
https://huntr.dev/bounties/129d6a4b-0504-4de1-a72c-3f12c4552343/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-6vf6-g3pr-j83h
- https://nvd.nist.gov/vuln/detail/CVE-2023-0323
- https://github.com/pimcore/pimcore/pull/13916.patch
- https://github.com/pimcore/pimcore/commit/746fac1a342841624f63ab13edcd340358e1bc04
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/129d6a4b-0504-4de1-a72c-3f12c4552343
