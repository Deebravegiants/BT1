# [H] Dive's improper processing of custom urls can lead to Remote Code Execution

## Summary
Severity: High
Advisory: CVE-2025-58176
Aliases: GHSA-2r34-7pgx-vvrc
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-09-03
Source: https://osv.dev/vulnerability/CVE-2025-58176
Type: osv

## Details
Dive is an open-source MCP Host Desktop Application that enables integration with function-calling LLMs. In versions 0.9.0 through 0.9.3, there is a one-click Remote Code Execution vulnerability triggered through a custom url value, `transport` in the JSON object. An attacker can exploit the vulnerability in the following two scenarios: a victim visits a malicious website controlled by the attacker and the website redirect to the URL automatically, or a victim clicks on such a crafted link embedded on a legitimate website (e.g., in user-generated content). In both cases, the browser invokes Dive's custom URL handler (dive:), which launches the Dive app and processes the crafted URL, leading to arbitrary code execution on the victim’s machine. This vulnerability is caused by improper processing of custom url. This is fixed in version 0.9.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/58xxx/CVE-2025-58176.json
- https://github.com/OpenAgentPlatform/Dive/security/advisories/GHSA-2r34-7pgx-vvrc
- https://nvd.nist.gov/vuln/detail/CVE-2025-58176
- https://github.com/OpenAgentPlatform/Dive/commit/acae6d40354d380f69f8241e9122a43ff64cff11
