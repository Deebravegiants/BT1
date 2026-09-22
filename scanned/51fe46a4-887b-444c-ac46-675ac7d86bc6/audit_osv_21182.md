# [C] CVE-2021-41110

## Summary
Severity: Critical
Advisory: CVE-2021-41110
Aliases: GHSA-7g7j-f5g3-fqp7
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-10-01
Source: https://osv.dev/vulnerability/CVE-2021-41110
Type: osv

## Details
cwlviewer is a web application to view and share Common Workflow Language workflows. Versions prior to 1.3.1 contain a Deserialization of Untrusted Data vulnerability. Commit number f6066f09edb70033a2ce80200e9fa9e70a5c29de (dated 2021-09-30) contains a patch. There are no available workarounds aside from installing the patch. The SnakeYaml constructor, by default, allows any data to be parsed. To fix the issue the object needs to be created with a `SafeConstructor` object, as seen in the patch.

## References
- https://github.com/common-workflow-language/cwlviewer/commit/f6066f09edb70033a2ce80200e9fa9e70a5c29de
- https://github.com/common-workflow-language/cwlviewer/security/advisories/GHSA-7g7j-f5g3-fqp7
- https://www.fatalerrors.org/a/analysis-of-the-snakeyaml-deserialization-in-java-security.html
