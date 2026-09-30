# [H] kyverno verifyImages rule bypass possible with malicious proxy/registry

## Summary
Severity: High
Advisory: GHSA-m3cq-xcx9-3gvm
CVE: CVE-2022-47633
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-21
Source: https://github.com/advisories/GHSA-m3cq-xcx9-3gvm
Type: github-advisory

## Affected
- Go: `github.com/kyverno/kyverno` — affected >=1.8.3 <1.8.5

## Details
### Impact

Users of Kyverno on versions 1.8.3 or 1.8.4 who use `verifyImages` rules to verify container image signatures, and do not prevent use of unknown registries.

### Patches

This issue has been fixed in version [1.8.5](https://github.com/kyverno/kyverno/releases/tag/v1.8.5)

### Workarounds

Configure a Kyverno policy to restrict registries to a set of secure trusted image registries ([sample](https://kyverno.io/policies/best-practices/restrict_image_registries/restrict_image_registries/)).

### References

## References
- https://github.com/kyverno/kyverno/security/advisories/GHSA-m3cq-xcx9-3gvm
- https://nvd.nist.gov/vuln/detail/CVE-2022-47633
- https://github.com/kyverno/kyverno/pull/5713
- https://github.com/kyverno/kyverno
- https://github.com/kyverno/kyverno/compare/v1.8.4...v1.8.5
- https://github.com/kyverno/kyverno/releases/tag/v1.8.5
- https://kyverno.io/docs/writing-policies/verify-images
- https://kyverno.io/policies/best-practices/restrict_image_registries/restrict_image_registries
- https://pkg.go.dev/vuln/GO-2022-1180
- https://web.archive.org/web/20230426095744/https://kyverno.io/policies/best-practices/restrict_image_registries/restrict_image_registries
