# [M] alf.io vulnerable to Arbitrary File Read and Exfil via simpleHttpClient Extension Script

## Summary
Severity: Medium
Advisory: CVE-2026-41412
Aliases: GHSA-6m62-53cw-4373
CVSS: 4.9 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-06-02
Source: https://osv.dev/vulnerability/CVE-2026-41412
Type: osv

## Details
alf.io is an open source ticket reservation system for conferences, trade shows, workshops, and meetups. Prior to version 2.0-M5-2606, the alf.io extension sandbox injects a fully-functional HTTP client (`simpleHttpClient`) into every extension script's scope. The `postFileAndSaveResponse()` method accepts an arbitrary filesystem path as its `file` parameter and reads the file contents using `new FileInputStream(file)` with no path validation, directory restriction, or allowlist. A malicious extension script can read any file accessible to the JVM process user and exfiltrate it to an attacker-controlled server via HTTP POST. Version 2.0-M5-2606 patches the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41412.json
- https://github.com/alfio-event/alf.io/security/advisories/GHSA-6m62-53cw-4373
- https://nvd.nist.gov/vuln/detail/CVE-2026-41412
