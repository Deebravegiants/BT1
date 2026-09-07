# [M] Crossplane-runtime contains Improper Input Validation via Compositions

## Summary
Severity: Medium
Advisory: GHSA-v829-x6hh-cqfq
CVE: CVE-2023-27484
CWE: CWE-20, CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:H/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-10
Source: https://github.com/advisories/GHSA-v829-x6hh-cqfq
Type: github-advisory

## Affected
- Go: `github.com/crossplane/crossplane` — affected >=0 <1.9.2
- Go: `github.com/crossplane/crossplane` — affected >=1.10.0 <1.10.3
- Go: `github.com/crossplane/crossplane` — affected >=1.11.0 <1.11.2

## Details
### Summary

Fuzz testing, by Ada Logics and sponsored by the CNCF, identified a [vulnerability](https://github.com/crossplane/crossplane-runtime/security/advisories/GHSA-vfvj-3m3g-m532) in the `fieldpath` package from `crossplane/crossplane-runtime` that an already highly privileged Crossplane user able to create or update Compositions could leverage to cause an out of memory panic in Crossplane.

### Details

Compositions allow users to specify patches inserting elements into arrays at an arbitrary index. When a Composition is selected for a Composite Resource, patches are evaluated and if a specified index is greater than the current size of the target slice, that slice's size will be increased to the specified index, which could lead to an excessive amount of memory usage and therefore the Pod being OOM-Killed. The index is already capped to the maximum value for a uint32 (4294967295) when parsed, but that is still an unnecessarily large value.

### Workaround

Users can restrict write privileges on Compositions to only admin users as a workaround.

## References
- https://github.com/crossplane/crossplane/security/advisories/GHSA-v829-x6hh-cqfq
- https://nvd.nist.gov/vuln/detail/CVE-2023-27484
- https://github.com/crossplane/crossplane
