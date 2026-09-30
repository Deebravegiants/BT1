# [H] ADB Explorer Vulnerable to Remote Code Execution via Insecure Deserialization

## Summary
Severity: High
Advisory: CVE-2026-26208
Aliases: GHSA-49qx-wpxj-p4mh
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-02-13
Source: https://osv.dev/vulnerability/CVE-2026-26208
Type: osv

## Details
ADB Explorer is a fluent UI for ADB on Windows. Prior to Beta 0.9.26020, ADB Explorer is vulnerable to Insecure Deserialization leading to Remote Code Execution. The application attempts to deserialize the App.txt settings file using Newtonsoft.Json with TypeNameHandling set to Objects. This allows an attacker to supply a crafted JSON file containing a gadget chain (e.g., ObjectDataProvider) to execute arbitrary code when the application launches and subsequently saves its settings. This vulnerability is fixed in Beta 0.9.26020.

## References
- https://github.com/Alex4SSB/ADB-Explorer/releases/tag/v0.9.26020
- https://github.com/Alex4SSB/ADB-Explorer/security/advisories/GHSA-49qx-wpxj-p4mh
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26208.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-26208
- https://github.com/Alex4SSB/ADB-Explorer/issues/294
- https://github.com/Alex4SSB/ADB-Explorer/commit/776f132cede86e1405520f2a28c78276dda5ab5a
