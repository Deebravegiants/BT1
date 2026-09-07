# [M] Mautic has Stored Cross-Site Scripting (XSS) in Project Option Selector

## Summary
Severity: Medium
Advisory: GHSA-5hvg-w58j-545m
CVE: CVE-2026-9811
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-5hvg-w58j-545m
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=7.0.0 <7.1.2

## Details
### Summary
A stored Cross-Site Scripting (XSS) vulnerability exists in the project selector component of Mautic 7. When rendering selection menus for associating projects with system entities, the application fails to sanitize project names returned via AJAX before injecting them into the DOM as option fields. An authenticated user with permissions to create projects can exploit this to store a malicious script payload in the project's name.

### Impact
When another administrative user subsequently opens an entity editor containing the project selector, the injected script executes within the context of their active browser session. This could allow an attacker to hijack the session, perform unauthorized state coordination, or access organizational data within the dashboard.

### Patched Versions
This security issue has been addressed in the following release:
* **7.1.2**

*Note: Mautic 6.x, 5.x, and 4.x branches do not contain the Projects feature or the associated AJAX selector and are not affected by this vulnerability. For general security support regarding legacy Mautic 4 releases, please refer to the [ELTS](https://mautic.org/extended-long-term-support-elts/) page.*

### Workarounds
There are no official workarounds. To mitigate this vulnerability without upgrading, restrict project creation and modification permissions to trusted administrative users.

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-5hvg-w58j-545m
- https://nvd.nist.gov/vuln/detail/CVE-2026-9811
- https://github.com/mautic/mautic
