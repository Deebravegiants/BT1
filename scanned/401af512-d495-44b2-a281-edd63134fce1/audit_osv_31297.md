# [H] Divide by Zero in ollama/ollama

## Summary
Severity: High
Advisory: CVE-2024-8063
Aliases: GHSA-2xf2-gjm6-g2c6, GO-2025-3689
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-03-20
Source: https://osv.dev/vulnerability/CVE-2024-8063
Type: osv

## Details
A divide by zero vulnerability exists in ollama/ollama version v0.3.3. The vulnerability occurs when importing GGUF models with a crafted type for `block_count` in the Modelfile. This can lead to a denial of service (DoS) condition when the server processes the model, causing it to crash.

## References
- https://huntr.com/bounties/fd8e1ed6-21d2-4c9e-8395-2098f11b7db9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/8xxx/CVE-2024-8063.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-8063
