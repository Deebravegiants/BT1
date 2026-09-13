# [H] Ollama Server Vulnerable to Denial of Service (DoS) Attack

## Summary
Severity: High
Advisory: GHSA-wrh5-cmwx-q2qr
CVE: CVE-2025-1975
CWE: CWE-129
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-05-16
Source: https://github.com/advisories/GHSA-wrh5-cmwx-q2qr
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0

## Details
A vulnerability in the Ollama server version 0.5.11 allows a malicious user to cause a Denial of Service (DoS) attack by customizing the manifest content and spoofing a service. This is due to improper validation of array index access when downloading a model via the /api/pull endpoint, which can lead to a server crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-1975
- https://github.com/ollama/ollama
- https://github.com/pypa/advisory-database/tree/main/vulns/ollama/PYSEC-2025-145.yaml
- https://huntr.com/bounties/921ba5d4-f1d0-4c66-9764-4f72dffe7acd
- https://pkg.go.dev/vuln/GO-2025-3695
