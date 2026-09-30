# [H] Tabby: Unsafe protocol handler execution via terminal linkifier allows arbitrary OS protocol invocation

## Summary
Severity: High
Advisory: CVE-2026-45037
Aliases: GHSA-cmpc-v2x9-j9x9
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L)
Published: 2026-05-15
Source: https://osv.dev/vulnerability/CVE-2026-45037
Type: osv

## Details
Tabby (formerly Terminus) is a highly configurable terminal emulator. Prior to 1.0.232, Tabby's terminal linkifier passes any detected URI directly to the operating system's protocol handler without validating the protocol scheme. This allows a malicious SSH or Telnet server to send crafted terminal output containing dangerous protocol URIs which Tabby renders as clickable links, triggering arbitrary OS protocol handlers on the victim's machine. This vulnerability is fixed in 1.0.232.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/45xxx/CVE-2026-45037.json
- https://github.com/Eugeny/tabby/security/advisories/GHSA-cmpc-v2x9-j9x9
- https://nvd.nist.gov/vuln/detail/CVE-2026-45037
