# [H] Possible image tampering from missing image validation for Packages

## Summary
Severity: High
Advisory: GHSA-pj4x-2xr5-w87m
CVE: CVE-2023-38495
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-07-28
Source: https://github.com/advisories/GHSA-pj4x-2xr5-w87m
Type: github-advisory

## Affected
- Go: `github.com/crossplane/crossplane` — affected >=0 <1.11.5
- Go: `github.com/crossplane/crossplane` — affected >=1.12.0 <1.12.3

## Details
### Impact

Crossplanes image backend does not validate the byte contents of Crossplane packages. As such, Crossplane does not detect if an attacker has tampered with a Package.

### Patches

The problem has been fixed in 1.11.5, 1.12.3 and 1.13.0, all the supported versions of Crossplane at the time of writing.

### Workarounds

Only using images from trusted sources and keeping Package editing/creating privileges to administrators only, which should be both considered already best practices.

### References

See `ADA-XP-23-11` in the Security Audit's [report](https://github.com/crossplane/crossplane/blob/ac8b24fe739c5d942ea885157148497f196c3dd3/security/ADA-security-audit-23.pdf).

### Credits

This was reported as `ADA-XP-23-11` by @AdamKorcz and @DavidKorczynski from Ada Logic and facilitated by OSTIF as part of the Security Audit sponsored by CNCF.

## References
- https://github.com/crossplane/crossplane/security/advisories/GHSA-pj4x-2xr5-w87m
- https://nvd.nist.gov/vuln/detail/CVE-2023-38495
- https://github.com/crossplane/crossplane
- https://github.com/crossplane/crossplane/blob/ac8b24fe739c5d942ea885157148497f196c3dd3/security/ADA-security-audit-23.pdf
