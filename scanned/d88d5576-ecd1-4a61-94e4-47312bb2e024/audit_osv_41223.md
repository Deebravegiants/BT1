# [C] GeoNetwork vulnerable to Remote Code Execution via unsafe Saxon XSLT processor configuration in formatter

## Summary
Severity: Critical
Advisory: CVE-2026-58400
Aliases: GHSA-x898-729x-cc3r
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-09-03
Source: https://osv.dev/vulnerability/CVE-2026-58400
Type: osv

## Details
GeoNetwork is a catalog application to manage spatially referenced resources. Prior to versions 4.4.12 and 4.2.17, the Saxon XSLT processor used to render formatters is configured without secure processing (`FEATURE_SECURE_PROCESSING`) and without disabling Java extension functions (`ALLOW_EXTERNAL_FUNCTIONS`). Any stylesheet loaded by GeoNetwork can therefore invoke
`java.lang.Runtime.exec()` or `java.lang.ProcessBuilder` directly, achieving arbitrary command execution as the GeoNetwork process user. A user with sufficient privileges to upload a formatter can deliver a `.xsl` file containing Java extension call that execute arbitrary OS commands with the privileges of the GeoNetwork process. The issue is patched in GeoNetwork versions 4.4.12 and 4.2.17.

## References
- https://docs.geonetwork-opensource.org/4.2/overview/change-log/version-4.2.17
- https://docs.geonetwork-opensource.org/4.4/overview/change-log/version-4.4.12
- https://thehackernews.com/2026/09/geonetwork-fixes-unauthenticated-rce.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/58xxx/CVE-2026-58400.json
- https://github.com/geonetwork/core-geonetwork/security/advisories/GHSA-x898-729x-cc3r
- https://nvd.nist.gov/vuln/detail/CVE-2026-58400
