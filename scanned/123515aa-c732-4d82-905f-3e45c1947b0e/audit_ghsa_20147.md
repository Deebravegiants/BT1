# [H] Path traversal mitigation bypass in OctoRPKI

## Summary
Severity: High
Advisory: GHSA-3jhm-87m6-x959
CWE: CWE-22
Ecosystem: Go
Published: 2022-06-25
Source: https://github.com/advisories/GHSA-3jhm-87m6-x959
Type: github-advisory

## Affected
- Go: `github.com/cloudflare/cfrpki` — affected >=0 <1.4.3

## Details
### Impact
The existing URI path filters in OctoRPKI (version < 1.4.3) mitigating Path traversal vulnerability could be bypassed by an attacker. In case a malicious TAL file is parsed, it was possible to write files outside the base cache folder.

### Specific Go Packages Affected
github.com/cloudflare/cfrpki/cmd/octorpki

### Patches
The issue was fixed in version 1.4.3

### References
[CVE-2021-3907](https://www.cvedetails.com/cve/CVE-2021-3907/)

## References
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-3jhm-87m6-x959
- https://github.com/cloudflare/cfrpki/security/advisories/GHSA-cqh2-vc2f-q4fh
- https://nvd.nist.gov/vuln/detail/CVE-2021-3907
- https://github.com/cloudflare/cfrpki
- https://github.com/cloudflare/cfrpki/releases/tag/v1.4.3
