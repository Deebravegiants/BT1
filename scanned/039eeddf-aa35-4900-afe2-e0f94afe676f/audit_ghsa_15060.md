# [H] crystals-go vulnerable to KyberSlash (timing side-channel attack for Kyber)

## Summary
Severity: High
Advisory: GHSA-f6jh-hvg2-9525
Ecosystem: Go
Published: 2024-01-17
Source: https://github.com/advisories/GHSA-f6jh-hvg2-9525
Type: github-advisory

## Affected
- Go: `github.com/kudelskisecurity/crystals-go` — affected >=0 <0.0.0-20240116172146-2a6ca2d4e64d

## Details
### Impact
On some platforms, when an attacker can time decapsulation of Kyber on forged cipher texts, they could possibly learn (parts of) the secret key.

### Patches
Patched in https://github.com/kudelskisecurity/crystals-go/pull/21

### Note
This library was written as part of a MsC student project in the Cybersecurity Team at Kudelski Security. It is not actively maintained anymore. It is only intended for research and testing. We discourage its use in any production environment. Kudelski Security does not use this library as part of their commercial offers or product. This has now been clarified on the project's README.

### References
https://groups.google.com/a/list.nist.gov/g/pqc-forum/c/ldX0ThYJuBo
http://kyberslash.cr.yp.to/

## References
- https://github.com/kudelskisecurity/crystals-go/security/advisories/GHSA-f6jh-hvg2-9525
- https://github.com/kudelskisecurity/crystals-go/issues/19
- https://github.com/kudelskisecurity/crystals-go/pull/20
- https://github.com/kudelskisecurity/crystals-go/pull/21
- https://github.com/kudelskisecurity/crystals-go/commit/2a6ca2d4e64d18dd6e8fbb4e48e22c2510118505
- https://github.com/kudelskisecurity/crystals-go
- https://kyberslash.cr.yp.to/faq
