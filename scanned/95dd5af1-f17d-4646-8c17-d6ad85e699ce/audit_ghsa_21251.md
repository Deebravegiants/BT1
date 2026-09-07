# [C] RCE vulnerability in Pimcore/Mail & Dynamic Text Layout

## Summary
Severity: Critical
Advisory: GHSA-5qxq-vgmm-q39m
CVE: CVE-2022-39365
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-29
Source: https://github.com/advisories/GHSA-5qxq-vgmm-q39m
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.9

## Details
### Impact
The user controlled twig templates rendering in `Pimcore/Mail` & `ClassDefinition\Layout\Text` is vulnerable to server-side template Injection RCE.

### Patches
Update to version 10.5.9 or apply this patch manually https://github.com/pimcore/pimcore/pull/13347.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/pull/13347.patch manually.

### References
Credits: @nth347 from Viettel Cyber Security

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-5qxq-vgmm-q39m
- https://nvd.nist.gov/vuln/detail/CVE-2022-39365
- https://github.com/pimcore/pimcore/pull/13347
- https://github.com/pimcore/pimcore/pull/13347.patch
- https://github.com/pimcore/pimcore/commit/43aa34e018f5cd447bceb864358285ba92f68372
- https://github.com/pimcore/pimcore
