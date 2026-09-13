# [M] Excessive Platform Resource Consumption within a Loop when unmarshalling Compose file having recursive loop

## Summary
Severity: Medium
Advisory: GHSA-36gq-35j3-p9r9
CVE: CVE-2024-10846
CWE: CWE-20, CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-36gq-35j3-p9r9
Type: github-advisory

## Affected
- Go: `github.com/compose-spec/compose-go/v2` — affected >=2.1.0 <2.4.1

## Details
### Impact
The `compose-go` library component in versions `v2.10-v2.4.0` allows an authorized user who sends malicious YAML payloads to cause the `compose-go` to consume excessive amount of Memory and CPU cycles while parsing YAML, such as used by Docker Compose from versions ` v2.27.0` to `v2.29.7` included

### Patches
compose-go `v2.24.1` fixed the issue

### Workarounds
There isn't any known workaround.

### References
* https://github.com/docker/compose/issues/12235
* https://github.com/compose-spec/compose-go/pull/703

* https://github.com/compose-spec/compose-go/pull/618
* https://github.com/docker/compose/commit/d239f0f3187a2ed5404c61f83bd5e995c81600ff#diff-33ef32bf6c23acb95f5902d7097b7a1d5128ca061167ec0716715b0b9eeaa5f6R10

## References
- https://github.com/compose-spec/compose-go/security/advisories/GHSA-36gq-35j3-p9r9
- https://nvd.nist.gov/vuln/detail/CVE-2024-10846
- https://github.com/docker/compose/issues/12235
- https://github.com/compose-spec/compose-go/pull/618
- https://github.com/compose-spec/compose-go/pull/703
- https://github.com/docker/compose/commit/d239f0f3187a2ed5404c61f83bd5e995c81600ff#diff-33ef32bf6c23acb95f5902d7097b7a1d5128ca061167ec0716715b0b9eeaa5f6R10
- https://github.com/compose-spec/compose-go
- https://security.netapp.com/advisory/ntap-20250425-0008
