# [M] Traefik has unexpected behavior with IPv4-mapped IPv6 addresses

## Summary
Severity: Medium
Advisory: GHSA-7jmw-8259-q9jx
CWE: CWE-180
Ecosystem: Go
Published: 2024-06-11
Source: https://github.com/advisories/GHSA-7jmw-8259-q9jx
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=3.0.0-beta3 <3.0.2
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.4
- Go: `github.com/traefik/traefik` — affected >=0 <2.11.4

## Details
### Impact

There is a vulnerability in [Go managing various Is methods (IsPrivate, IsLoopback, etc) for IPv4-mapped IPv6 addresses](https://groups.google.com/g/golang-announce/c/XbxouI9gY7k/m/TuoGEhxIEwAJ).

They didn't work as expected returning false for addresses which would return true in their traditional IPv4 forms.

### References

- [CVE-2024-24790](https://www.cve.org/CVERecord?id=CVE-2024-24790)

### Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.4
- https://github.com/traefik/traefik/releases/tag/v3.0.2

### Workarounds

No workaround.

### For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-7jmw-8259-q9jx
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.4
- https://github.com/traefik/traefik/releases/tag/v3.0.2
- https://pkg.go.dev/vuln/GO-2024-2917
- https://www.cve.org/CVERecord?id=CVE-2024-24790
