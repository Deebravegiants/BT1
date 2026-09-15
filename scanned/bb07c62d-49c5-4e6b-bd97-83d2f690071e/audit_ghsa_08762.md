# [M] in-toto-golang and in-toto-python have inconsistent negation behavior

## Summary
Severity: Medium
Advisory: GHSA-pmwq-pjrm-6p5r
CWE: CWE-168
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-05-08
Source: https://github.com/advisories/GHSA-pmwq-pjrm-6p5r
Type: github-advisory

## Affected
- Go: `github.com/in-toto/in-toto-golang` — affected >=0 <0.11.0

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_

in-toto-golang and in-toto-python both support glob patterns in artifact rules to indicate the artifacts that a rule applies to. Both support negations in character classes to indicate what should *not* be matched, but they used different operators to indicate the negation. in-toto-python uses `!` while in-toto-golang used `^`. A layout authored with the expectations of one implementation can therefore exhibit different behavior in the other implementation.

This impacts users in a specific set of circumstances where two different implementations are used to verify the same layout + attestation bundle at different stages of the same pipeline. As a rule of thumb, we advise using a single implementation across all aspects of a pipeline, from layout creation to pipeline execution and verification to prevent this class of bugs.

### Patches
_Has the problem been patched? What versions should users upgrade to?_

in-toto-golang has been updated to use `!` instead of `^` to indicate negation. See https://github.com/in-toto/in-toto-golang/pull/462. This is part of v0.11.0.

## References
- https://github.com/in-toto/in-toto-golang/security/advisories/GHSA-pmwq-pjrm-6p5r
- https://github.com/in-toto/in-toto-golang/pull/462
- https://github.com/in-toto/in-toto-golang/commit/36d782ffb2ca3adbffcdce1fd971c23319dd4469
- https://github.com/in-toto/in-toto-golang
