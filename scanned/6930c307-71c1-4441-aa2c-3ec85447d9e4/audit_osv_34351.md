# [C] Volkov Labs Business Links plugin vulnerable to privilege escalation attack

## Summary
Severity: Critical
Advisory: CVE-2025-58746
Aliases: GHSA-93qj-gv4p-mf53
CVSS: 9.0 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-09-08
Source: https://osv.dev/vulnerability/CVE-2025-58746
Type: osv

## Details
The Volkov Labs Business Links panel for Grafana provides an interface to navigate using external links, internal dashboards, time pickers, and dropdown menus. Prior to version 2.4.0, a malicious actor with Editor privileges can escalate their privileges to Administrator and perform arbitrary administrative actions. This is possible because the plugin allows arbitrary JavaScript code injection in the [Layout] → [Link] → [URL] field. Version 2.4.0 contains a fix for the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58746.json
- https://github.com/VolkovLabs/business-links/security/advisories/GHSA-93qj-gv4p-mf53
- https://nvd.nist.gov/vuln/detail/CVE-2025-58746
- https://github.com/VolkovLabs/business-links/commit/9d203a6950de7860e11b25e4265ed8fe60082d7d
