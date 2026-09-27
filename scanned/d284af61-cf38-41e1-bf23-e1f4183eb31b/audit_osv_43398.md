# [C] FreePBX: Authenticated TTS AGI Command Injection Through TTS Name

## Summary
Severity: Critical
Advisory: CVE-2026-73660
Aliases: GHSA-hg3v-m857-mvw9
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-13
Source: https://osv.dev/vulnerability/CVE-2026-73660
Type: osv

## Details
FreePBX is an open source IP PBX. Prior to 16.0.6 and 17.0.5.4, the FreePBX Text-To-Speech module allows an authenticated administrator to save a TTS destination name that is HTML-encoded for storage, decoded during dialplan generation, passed as an AGI argument, and used to build filenames inside agi-bin/propolys-tts.agi. The TTS destination name reaches a raw shell-command execution path, allowing arbitrary operating-system command execution as the asterisk service user. This issue is fixed in versions 16.0.6 and 17.0.5.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/73xxx/CVE-2026-73660.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-hg3v-m857-mvw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-73660
- https://github.com/FreePBX/tts/commit/37cf0dd3e9ceb4a32e09a2fca6a145320245c0a0
- https://github.com/FreePBX/tts/commit/4057410439e66d8be2b47c6358de5fab498bbc21
