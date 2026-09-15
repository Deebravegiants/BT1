# [C] Cross-Site WebSocket Hijacking (CSWSH) in automatic1111/stable-diffusion-webui

## Summary
Severity: Critical
Advisory: CVE-2024-11045
CVSS: 9.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-11045
Type: osv

## Details
A Cross-Site WebSocket Hijacking (CSWSH) vulnerability in automatic1111/stable-diffusion-webui version 1.10.0 allows an attacker to clone a malicious server extension from a GitHub repository. The vulnerability arises from the lack of proper validation on WebSocket connections at ws://127.0.0.1:7860/queue/join, enabling unauthorized actions on the server. This can lead to unauthorized cloning of server extensions, execution of malicious scripts, data exfiltration, and potential denial of service (DoS).

## References
- https://huntr.com/bounties/b7ed0d87-0be5-4526-9b21-ffe0d39c283e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11045.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11045
