# [M] labsai/eddi Vulnerable to Path Traversal (Zip Slip) in ZIP Import Function

## Summary
Severity: Medium
Advisory: CVE-2025-32779
Aliases: GHSA-9v34-frgq-63mv
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32779
Type: osv

## Details
E.D.D.I (Enhanced Dialog Driven Interface) is a middleware to connect and manage LLM API bots. In versions before 5.5.0, an attacker with access to the `/backup/import` API endpoint can write arbitrary files to locations outside the intended extraction directory due to a Zip Slip vulnerability. Although the application runs as a non-root user (`185`), limiting direct impact on system-level files, this vulnerability can still be exploited to overwrite application files (e.g., JAR libraries) owned by the application user. This overwrite can potentially lead to Remote Code Execution (RCE) within the application's context. This issue has been patched in version 5.5.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32779.json
- https://github.com/labsai/EDDI/security/advisories/GHSA-9v34-frgq-63mv
- https://nvd.nist.gov/vuln/detail/CVE-2025-32779
- https://github.com/labsai/EDDI/commit/1e207d0e4f72a5a93920bc0f76cad53ffd8e7065
- https://www.sonarsource.com/blog/code-security-for-conversational-ai-uncovering-a-zip-slip-in-eddi
