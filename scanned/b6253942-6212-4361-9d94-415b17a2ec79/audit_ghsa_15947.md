# [H] OpenRefine has a path traversal in LoadLanguageCommand

## Summary
Severity: High
Advisory: GHSA-qfwq-6jh6-8xx4
CVE: CVE-2024-49760
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2024-10-24
Source: https://github.com/advisories/GHSA-qfwq-6jh6-8xx4
Type: github-advisory

## Affected
- Maven: `org.openrefine:openrefine` — affected >=0 <3.8.3

## Details
The load-language command expects a `lang` parameter from which it constructs the path of the localization file to load, of the form `translations-$LANG.json`.
When doing so, it does not check that the resulting path is in the expected directory, which means that this command could be exploited to read other JSON files on the file system.

The command should be patched by checking that the normalized path is in the expected directory.

## References
- https://github.com/OpenRefine/OpenRefine/security/advisories/GHSA-qfwq-6jh6-8xx4
- https://nvd.nist.gov/vuln/detail/CVE-2024-49760
- https://github.com/OpenRefine/OpenRefine/commit/24d084052dc55426fe460f2a17524fd18d28b20c
- https://github.com/OpenRefine/OpenRefine
