# [H] CVE-2026-9081

## Summary
Severity: High
Advisory: CVE-2026-9081
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N)
Published: 2026-08-05
Source: https://osv.dev/vulnerability/CVE-2026-9081
Type: osv

## Details
IBM Langflow OSS 1.0.0 through 1.10.3, and 1.0.0 through 1.10.3 contains a Server-Side Request Forgery (SSRF) vulnerability in the validate_model_provider_key() function for the Ollama provider. The function accepts a user-supplied OLLAMA_BASE_URL parameter and passes it directly to requests.get() without validation, scheme/host allowlisting, or filtering of private IP ranges (loopback, RFC1918, link-local addresses).

## References
- https://www.ibm.com/support/pages/node/7282650
