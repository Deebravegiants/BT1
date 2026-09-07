# [M] Pimcore Cross-site Scripting (XSS) in Static Routes name field

## Summary
Severity: Medium
Advisory: GHSA-mhpj-7m7h-8p6x
CVE: CVE-2023-2616
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2023-05-11
Source: https://github.com/advisories/GHSA-mhpj-7m7h-8p6x
Type: github-advisory

## Affected
- Packagist: `pimcore/pimcore` — affected >=0 <10.5.21

## Details
### Impact
This vulnerability has the potential to steal a user's cookie and gain unauthorized access to that user's account through the stolen cookie or redirect users to other malicious sites.


### Patches
Update to version 10.5.21 or apply this patch manually:
https://github.com/pimcore/pimcore/commit/07a2c95be524c7e20105cef58c5767d4ebb06091.patch

### Workarounds
Apply patches manually:
https://github.com/pimcore/pimcore/commit/07a2c95be524c7e20105cef58c5767d4ebb06091.patch

### References
https://huntr.dev/bounties/564cb512-2bcc-4458-8c20-88110ab45801/

## References
- https://github.com/pimcore/pimcore/security/advisories/GHSA-mhpj-7m7h-8p6x
- https://nvd.nist.gov/vuln/detail/CVE-2023-2616
- https://github.com/pimcore/pimcore/commit/07a2c95be524c7e20105cef58c5767d4ebb06091
- https://github.com/pimcore/pimcore
- https://huntr.dev/bounties/564cb512-2bcc-4458-8c20-88110ab45801
