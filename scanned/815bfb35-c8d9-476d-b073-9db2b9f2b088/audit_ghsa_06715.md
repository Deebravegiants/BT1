# [C] Mautic vulnerable to Path Traversal via Campaign Import

## Summary
Severity: Critical
Advisory: GHSA-6r9h-4h75-7q4x
CVE: CVE-2026-9559
CWE: CWE-22, CWE-73, CWE-98
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-6r9h-4h75-7q4x
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=7.0.0 <7.1.2

## Details
### Summary
A path traversal vulnerability exists in the campaign import feature of Mautic 7. When extracting uploaded ZIP files during campaign imports, a flaw in the validation logic allows file paths to escape the intended temporary directories. 

### Impact
An authenticated user with campaign import privileges (`campaign:imports:create`) can write arbitrary PHP files to sensitive system directories. An attacker can exploit this to overwrite critical internal configuration or cache components, resulting in Remote Code Execution (RCE) under the context of the web server user.

### Patched Versions
This security issue has been addressed in the following release:
* **7.1.2**

*Note: Mautic 6.x, 5.x, and 4.x branches are not affected by this vulnerability. For general security support regarding legacy Mautic 4 releases, please refer to the [ELTS](https://mautic.org/extended-long-term-support-elts/) page.*

### Workarounds
There are no official workarounds. To mitigate this risk without upgrading, revoke campaign import permissions (`campaign:imports:create`) from non-administrative users.

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-6r9h-4h75-7q4x
- https://nvd.nist.gov/vuln/detail/CVE-2026-9559
- https://github.com/mautic/mautic
