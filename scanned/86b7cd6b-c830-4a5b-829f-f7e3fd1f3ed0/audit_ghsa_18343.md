# [M] Dragonfly vulnerable to timing attacks against Proxy’s basic authentication

## Summary
Severity: Medium
Advisory: GHSA-c2fc-9q9c-5486
CVE: CVE-2025-59350
CWE: CWE-208, CWE-697
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-09-17
Source: https://github.com/advisories/GHSA-c2fc-9q9c-5486
Type: github-advisory

## Affected
- Go: `github.com/dragonflyoss/dragonfly` — affected >=0 <2.1.0
- Go: `d7y.io/dragonfly/v2` — affected >=0 <2.1.0

## Details
### Impact
The access control mechanism for the Proxy feature uses simple string comparisons and is therefore vulnerable to timing attacks. An attacker may try to guess the password one character at a time by sending all possible characters to a vulnerable mechanism and measuring the comparison instruction’s execution times.
The vulnerability is shown in figure 8.1, where both the username and password are compared with a short-circuiting equality operation.

```golang
if user != proxy.basicAuth.Username || pass != proxy.basicAuth.Password {
```

It is currently undetermined what an attacker may be able to do with access to the proxy password.

### Patches

- Dragonfy v2.1.0 and above.

### Workarounds

There are no effective workarounds, beyond upgrading.

### References

A third party security audit was performed by Trail of Bits, you can see the [full report](https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf).

If you have any questions or comments about this advisory, please email us at [dragonfly-maintainers@googlegroups.com](mailto:dragonfly-maintainers@googlegroups.com).

## References
- https://github.com/dragonflyoss/dragonfly/security/advisories/GHSA-c2fc-9q9c-5486
- https://nvd.nist.gov/vuln/detail/CVE-2025-59350
- https://github.com/dragonflyoss/dragonfly
- https://github.com/dragonflyoss/dragonfly/blob/main/docs/security/dragonfly-comprehensive-report-2023.pdf
- https://pkg.go.dev/vuln/GO-2025-3972
