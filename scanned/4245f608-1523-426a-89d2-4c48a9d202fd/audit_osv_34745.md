# [H] Open WebUI Affected by an External Model Server (Direct Connections) Code Injection via SSE Events

## Summary
Severity: High
Advisory: CVE-2025-64496
Aliases: GHSA-cm35-v4vp-5xvx, PYSEC-2026-1729
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:N)
Published: 2025-11-08
Source: https://osv.dev/vulnerability/CVE-2025-64496
Type: osv

## Details
Open WebUI is a self-hosted artificial intelligence platform designed to operate entirely offline. Versions 0.6.224 and prior contain a code injection vulnerability in the Direct Connections feature that allows malicious external model servers to execute arbitrary JavaScript in victim browsers via Server-Sent Event (SSE) execute events. This leads to authentication token theft, complete account takeover, and when chained with the Functions API, enables remote code execution on the backend server. The attack requires the victim to enable Direct Connections (disabled by default) and add the attacker's malicious model URL, achievable through social engineering of the admin and subsequent users. This issue is fixed in version 0.6.35.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64496.json
- https://github.com/open-webui/open-webui/security/advisories/GHSA-cm35-v4vp-5xvx
- https://nvd.nist.gov/vuln/detail/CVE-2025-64496
- https://github.com/open-webui/open-webui/commit/8af6a4cf21b756a66cd58378a01c60f74c39b7ca
