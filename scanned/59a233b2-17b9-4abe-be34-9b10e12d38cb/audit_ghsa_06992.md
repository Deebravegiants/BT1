# [H] Mautic has Stored Cross-Site Scripting (XSS) in Projects Component

## Summary
Severity: High
Advisory: GHSA-7h65-whp7-rgqf
CVE: CVE-2026-9809
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:H/A:N (CVSS_V3)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-7h65-whp7-rgqf
Type: github-advisory

## Affected
- Packagist: `mautic/core` — affected >=7.0.0 <7.1.2

## Details
### Summary
A stored Cross-Site Scripting (XSS) vulnerability exists in the Projects component of Mautic 7. When displaying project tags and popovers on administrative detail views (such as campaigns, emails, or forms), user-supplied project names are rendered without proper sanitization. An authenticated user with permissions to create or edit projects can exploit this to inject malicious script payloads.

### Impact
When an administrative user views an entity associated with a compromised project and hovers over its tag, the injected script executes within the context of their active browser session. This could allow an attacker to perform administrative actions on behalf of the victim, alter system configurations, or exfiltrate sensitive data.

### Patched Versions
This security issue has been addressed in the following release:
* **7.1.2**

*Note: Mautic 6.x, 5.x, and 4.x branches do not contain the Projects feature and are not affected by this vulnerability. For general security support regarding legacy Mautic 4 releases, please refer to the [ELTS](https://mautic.org/extended-long-term-support-elts/) page.*

### Workarounds
There are no official workarounds. To mitigate this vulnerability without upgrading, restrict project creation and modification permissions to trusted administrative users.

## References
- https://github.com/mautic/mautic/security/advisories/GHSA-7h65-whp7-rgqf
- https://nvd.nist.gov/vuln/detail/CVE-2026-9809
- https://github.com/mautic/mautic
