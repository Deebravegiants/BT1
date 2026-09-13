# [H] CVE-2025-66960

## Summary
Severity: High
Advisory: CVE-2025-66960
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-21
Source: https://osv.dev/vulnerability/CVE-2025-66960
Type: osv

## Details
An issue in ollama v.0.12.10 allows a remote attacker to cause a denial of service via the fs/ggml/gguf.go, function readGGUFV1String reads a string length from untrusted GGUF metadata

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/66xxx/CVE-2025-66960.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-66960
- https://github.com/ollama/ollama/issues/9820
- https://zero.shotlearni.ng/blog/cve-2025-66960guf-v1-string-length-cause-panic-in-readggufv1string/
