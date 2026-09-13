# [H] Moby Race Condition vulnerability

## Summary
Severity: High
Advisory: GHSA-2mj3-vfvx-fc43
CVE: CVE-2024-36621
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-11-29
Source: https://github.com/advisories/GHSA-2mj3-vfvx-fc43
Type: github-advisory

## Affected
- Go: `github.com/moby/moby` — affected >=0 <26.0.0

## Details
moby v25.0.5 is affected by a Race Condition in builder/builder-next/adapters/snapshot/layer.go. The vulnerability could be used to trigger concurrent builds that call the EnsureLayer function resulting in resource leaks/exhaustion.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36621
- https://github.com/moby/moby/commit/37545cc644344dcb576cba67eb7b6f51a463d31e
- https://gist.github.com/1047524396/5d44459edab5fafcdf86b43909b81135
- https://github.com/advisories/GHSA-2mj3-vfvx-fc43
- https://github.com/moby/moby
- https://github.com/moby/moby/blob/v25.0.5/builder/builder-next/adapters/snapshot/layer.go#L24
