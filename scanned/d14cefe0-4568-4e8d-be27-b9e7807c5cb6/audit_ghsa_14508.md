# [H] Improper quoting of columns when calling methods "getByUuid" & "exists" on UUID Model

## Summary
Severity: High
Advisory: GHSA-xc9p-r5qj-8xm9
CVE: CVE-2023-28108
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2023-03-17
Source: https://github.com/advisories/GHSA-xc9p-r5qj-8xm9
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.19

## Details
### Impact

The quoting is not done properly in UUID DAO model, so there's the theoretical possibility to inject custom SQL if the developer is using this methods with input data and not doing proper input validation in advance and so relies on the auto-quoting being done by the DAO class.

### Patches
Update to version 10.5.19 or apply this patch manually https://github.com/pimcore/pimcore/commit/08e7ba56ae983c3c67ec563b6989b16ef8f35275.patch

### Workarounds
Apply https://github.com/pimcore/pimcore/commit/08e7ba56ae983c3c67ec563b6989b16ef8f35275.patch manually.

### References
#14633

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-xc9p-r5qj-8xm9
- https://nvd.nist.gov/vuln/detail/CVE-2023-28108
- https://github.com/pimcore/pimcore/pull/14633
- https://github.com/pimcore/pimcore/commit/08e7ba56ae983c3c67ec563b6989b16ef8f35275.patch
- https://github.com/pimcore/pimcore
