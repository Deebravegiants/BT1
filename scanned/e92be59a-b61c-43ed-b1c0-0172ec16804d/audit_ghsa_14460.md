# [M] Pimcore Remote Code Execution vulnerability in Search function

## Summary
Severity: Medium
Advisory: GHSA-42c3-wvww-gcqj
CVE: CVE-2023-1578
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-03-22
Source: https://github.com/advisories/GHSA-42c3-wvww-gcqj
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.19

## Details
### Impact
Attacker can get full DB and maybe RCE knowing the WEBROOT path

### Patches
Update to version 10.5.19 or apply this patch manually https://github.com/pimcore/pimcore/commit/367b74488808d71ec3f66f4ca9e8df5217c2c8d2.patch

### Workarounds
Apply patch https://github.com/pimcore/pimcore/commit/367b74488808d71ec3f66f4ca9e8df5217c2c8d2.patch manually.

### References
#14538

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-42c3-wvww-gcqj
- https://nvd.nist.gov/vuln/detail/CVE-2023-1578
- https://github.com/pimcore/pimcore/pull/14538
- https://github.com/pimcore/pimcore/commit/367b74488808d71ec3f66f4ca9e8df5217c2c8d2
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/7e441a14-8e55-4ab4-932c-4dc56bb1bc2e
