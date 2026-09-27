# [M] Squidex has Blind SSRF via file:// Protocol in Restore API leading to Local File Interaction

## Summary
Severity: Medium
Advisory: CVE-2026-41177
Aliases: GHSA-45fq-w37p-qfw5
CVSS: 5.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:L)
Published: 2026-04-22
Source: https://osv.dev/vulnerability/CVE-2026-41177
Type: osv

## Details
Squidex is an open source headless content management system and content management hub. Prior to version 7.23.0, the Squidex Restore API is vulnerable to Blind Server-Side Request Forgery (SSRF). The application fails to validate the URI scheme of the user-supplied `Url` parameter, allowing the use of the `file://` protocol. This allows an authenticated administrator to force the backend server to interact with the local filesystem, which can lead to Local File Interaction (LFI) and potential disclosure of sensitive system information through side-channel analysis of internal logs. Version 7.23.0 contains a fix.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41177.json
- https://github.com/Squidex/squidex/security/advisories/GHSA-45fq-w37p-qfw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-41177
- https://github.com/Squidex/squidex/commit/b81d75e1d9c1a8e30993c2ee59b350002b9aeda4
