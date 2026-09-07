# [M]  Formwork has a cross-site scripting (XSS) vulnerability in Site title

## Summary
Severity: Medium
Advisory: GHSA-vf6x-59hh-332f
CWE: CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-03-01
Source: https://github.com/advisories/GHSA-vf6x-59hh-332f
Type: github-advisory

## Affected
- Packagist: `getformwork/formwork` — affected >=2.0.0-beta.3 <2.0.0-beta.4

## Details
### Summary

The site title field at /panel/options/site/allows embedding JS tags, which can be used to attack all members of the system. This is a widespread attack and can cause significant damage if there is a considerable number of users.

### Impact

The attack is widespread, leveraging what XSS can do. This will undoubtedly impact system availability.

### Patches
- [**Formwork 2.x** (aa3e9c6)](https://github.com/getformwork/formwork/commit/aa3e9c684035d9e8495169fde7c57d97faa3f9a2) escapes site title from panel header navigation.

### Details

By embedding "<!--", the source code can be rendered non-functional, significantly impacting system availability. However, the attacker would need admin privileges, making the attack more difficult to execute.

## References
- https://github.com/getformwork/formwork/security/advisories/GHSA-vf6x-59hh-332f
- https://github.com/getformwork/formwork/commit/aa3e9c684035d9e8495169fde7c57d97faa3f9a2
- https://github.com/getformwork/formwork
