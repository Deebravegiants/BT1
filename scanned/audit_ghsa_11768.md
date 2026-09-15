# [M] Fonoster is vulnerable to directory traversal

## Summary
Severity: Medium
Advisory: GHSA-9fv2-c7v6-p45w
CVE: CVE-2024-43035
CWE: CWE-24
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2026-03-05
Source: https://github.com/advisories/GHSA-9fv2-c7v6-p45w
Type: github-advisory

## Affected
- npm: `@fonoster/voice` — affected >=0.5.5 <0.6.1

## Details
Fonoster 0.5.5 before 0.6.1 allows ../ directory traversal to read arbitrary files via the /sounds/:file or /tts/:file VoiceServer endpoint. This occurs in serveFiles in mods/voice/src/utils.ts. NOTE: serveFiles exists in 0.5.5 but not in the next release, 0.6.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43035
- https://github.com/fonoster/fonoster
- https://github.com/fonoster/fonoster/blob/4a1438d9dedeaf7b2a5b6a50d5e233f994e2b2cf/mods/voice/src/utils.ts#L66-L70
- https://zeropath.com/blog/fonoster-voiceserver-lfi-vulnerability
