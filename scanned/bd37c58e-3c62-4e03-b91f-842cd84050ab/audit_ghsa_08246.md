# [H] Ollama contains a heap out-of-bounds read vulnerability in the GGUF model loader

## Summary
Severity: High
Advisory: GHSA-x8qc-fggm-mpqg
CVE: CVE-2026-7482
CWE: CWE-125
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-x8qc-fggm-mpqg
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0 <0.17.1

## Details
Ollama before 0.17.1 contains a heap out-of-bounds read vulnerability in the GGUF model loader. The /api/create endpoint accepts an attacker-supplied GGUF file in which the declared tensor offset and size exceed the file's actual length; during quantization in fs/ggml/gguf.go and server/quantization.go (WriteTo()), the server reads past the allocated heap buffer. The leaked memory contents may include environment variables, API keys, system prompts, and concurrent users' conversation data, and can be exfiltrated by uploading the resulting model artifact through the /api/push endpoint to an attacker-controlled registry. The /api/create and /api/push endpoints have no authentication in the upstream distribution. Default deployments bind to 127.0.0.1, but the documented OLLAMA_HOST=0.0.0.0 configuration is widely used in practice (large public-internet exposure observed).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-7482
- https://github.com/ollama/ollama/pull/14406
- https://github.com/ollama/ollama/commit/88d57d0483cca907e0b23a968c83627a20b21047
- https://github.com/ollama/ollama
- https://github.com/ollama/ollama/releases/tag/v0.17.1
