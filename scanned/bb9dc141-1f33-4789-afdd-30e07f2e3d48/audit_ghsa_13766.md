# [H] ZITADEL race condition in lockout policy execution

## Summary
Severity: High
Advisory: GHSA-7h8m-vrxx-vr4m
CVE: CVE-2023-47111
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-11-08
Source: https://github.com/advisories/GHSA-7h8m-vrxx-vr4m
Type: github-advisory

## Affected
- Go: `github.com/zitadel/zitadel` — affected >=2.39.0 <2.40.5
- Go: `github.com/zitadel/zitadel` — affected >=0 <2.38.3

## Details
### Impact

ZITADEL provides administrators the possibility to define a `Lockout Policy` with a maximum amount of failed password check attempts. On every failed password check, the amount of failed checks is compared against the configured maximum.
Exceeding the limit, will lock the user and prevent further authentication.

In the affected implementation it was possible for an attacker to start multiple parallel password checks, giving him the possibility to try out more combinations than configured in the `Lockout Policy`.

### Patches

2.x versions are fixed on >= [2.40.5](https://github.com/zitadel/zitadel/releases/tag/v2.40.5)
2.38.x versions are fixed on >= [2.38.3](https://github.com/zitadel/zitadel/releases/tag/v2.38.3)

### Workarounds

There is no workaround since a patch is already available.

### References

None

### Questions

If you have any questions or comments about this advisory, please email us at [security@zitadel.com](mailto:security@zitadel.com)

## References
- https://github.com/zitadel/zitadel/security/advisories/GHSA-7h8m-vrxx-vr4m
- https://nvd.nist.gov/vuln/detail/CVE-2023-47111
- https://github.com/zitadel/zitadel/commit/22e2d5599918864877e054ebe82fb834a5aa1077
- https://github.com/zitadel/zitadel
- https://github.com/zitadel/zitadel/releases/tag/v2.38.3
- https://github.com/zitadel/zitadel/releases/tag/v2.40.5
