# [M] Ollama does not validate the format of the digest (sha256 with 64 hex digits)

## Summary
Severity: Medium
Advisory: GHSA-8hqg-whrw-pv92
CVE: CVE-2024-37032
Ecosystem: Go
Published: 2024-05-31
Source: https://github.com/advisories/GHSA-8hqg-whrw-pv92
Type: github-advisory

## Affected
- Go: `github.com/ollama/ollama` — affected >=0 <0.1.34

## Details
Ollama before 0.1.34 does not validate the format of the digest (sha256 with 64 hex digits) when getting the model path, and thus mishandles the TestGetBlobsPath test cases such as fewer than 64 hex digits, more than 64 hex digits, or an initial `../` substring.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37032
- https://github.com/ollama/ollama/pull/4175
- https://github.com/ollama/ollama/commit/2a21363bb756a7341d3d577f098583865bd7603f
- https://github.com/advisories/GHSA-8hqg-whrw-pv92
- https://github.com/ollama/ollama
- https://github.com/ollama/ollama/blob/adeb40eaf29039b8964425f69a9315f9f1694ba8/server/modelpath_test.go#L41-L58
- https://github.com/ollama/ollama/compare/v0.1.33...v0.1.34
- https://pkg.go.dev/vuln/GO-2024-2901
- https://www.vicarius.io/vsociety/posts/probllama-in-ollama-a-tale-of-a-yet-another-rce-vulnerability-cve-2024-37032
