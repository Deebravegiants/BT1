# [M] Outline Affected an Arbitrary File Read via Path Traversal in JSON Import

## Summary
Severity: Medium
Advisory: CVE-2026-25062
Aliases: GHSA-7r4f-3wjv-83xf
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-02-11
Source: https://osv.dev/vulnerability/CVE-2026-25062
Type: osv

## Details
Outline is a service that allows for collaborative documentation. Prior to 1.4.0, during the JSON import process, the value of attachments[].key from the imported JSON is passed directly to path.join(rootPath, node.key) and then read using fs.readFile without validation. By embedding path traversal sequences such as ../ or absolute paths, an attacker can read arbitrary files on the server and import them as attachments. This vulnerability is fixed in 1.4.0.

## References
- https://github.com/outline/outline/releases/tag/v1.4.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25062.json
- https://github.com/outline/outline/security/advisories/GHSA-7r4f-3wjv-83xf
- https://nvd.nist.gov/vuln/detail/CVE-2026-25062
