# [H] github.com/russellhaering/gosaml2 is vulnerable to NULL Pointer Dereference

## Summary
Severity: High
Advisory: GHSA-prjq-f4q3-fvfr
CVE: CVE-2020-7731
CWE: CWE-476
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-11-15
Source: https://github.com/advisories/GHSA-prjq-f4q3-fvfr
Type: github-advisory

## Affected
- Go: `github.com/russellhaering/gosaml2` — affected >=0 <0.7.0
- Go: `github.com/russellhaering/goxmldsig` — affected >=0 <1.1.1

## Details
### Impact
In versions prior to v0.7.0 it was possible for an attacker to supply an invalid assertion which would trigger a panic due to a nil-pointer dereference.

### Patches
The issue was patched in v0.7.0, released on March 2, 2022.

### Workarounds
Callers to `gosaml2` can use `recover()` to handle panics to mitigate a potential DoS.

### References
See issue [#59](https://github.com/russellhaering/gosaml2/issues/59) for details.

## References
- https://github.com/russellhaering/gosaml2/security/advisories/GHSA-prjq-f4q3-fvfr
- https://github.com/russellhaering/gosaml2/issues/59
- https://github.com/russellhaering/goxmldsig/issues/48
- https://github.com/russellhaering/gosaml2/pull/90
- https://github.com/russellhaering/gosaml2/commit/66e3b7affd622b8b24ea1e18845f045e46b23424
- https://github.com/russellhaering/gosaml2
- https://github.com/russellhaering/gosaml2/releases/tag/v0.7.0
- https://snyk.io/vuln/SNYK-GOLANG-GITHUBCOMRUSSELLHAERINGGOSAML2-608302
