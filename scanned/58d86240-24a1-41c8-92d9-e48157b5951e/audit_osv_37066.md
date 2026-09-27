# [C] FreePBX: Command Injection leading to Remote Code Execution in FreePBX ElevenLabs Text-to-Speech integration

## Summary
Severity: Critical
Advisory: CVE-2026-28209
Aliases: GHSA-f558-mp87-58vj
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-05
Source: https://osv.dev/vulnerability/CVE-2026-28209
Type: osv

## Details
FreePBX is an open source IP PBX. From versions 16.0.17.2 to before 16.0.20 and from version 17.0.2.4 to before 17.0.5, a command injection vulnerability exists in FreePBX when using the ElevenLabs Text-to-Speech (TTS) engine in the recordings module. This issue has been patched in versions 16.0.20 and 17.0.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/28xxx/CVE-2026-28209.json
- https://github.com/FreePBX/security-reporting/security/advisories/GHSA-f558-mp87-58vj
- https://nvd.nist.gov/vuln/detail/CVE-2026-28209
