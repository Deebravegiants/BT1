# [M] ACME DNS: Azure Identity Libraries Elevation of Privilege Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-rvj4-q8q5-8grf
CWE: CWE-362
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-20
Source: https://github.com/advisories/GHSA-rvj4-q8q5-8grf
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.0.3
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.5

## Details
### Impact

There is a vulnerability in [Azure Identity Libraries and Microsoft Authentication Library Elevation of Privilege Vulnerability](https://nvd.nist.gov/vuln/detail/CVE-2024-35255).

### References

- [CVE-2024-35255](https://nvd.nist.gov/vuln/detail/CVE-2024-35255)

### Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.5
- https://github.com/traefik/traefik/releases/tag/v3.0.3

### Workarounds

No workaround.

### For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-rvj4-q8q5-8grf
- https://nvd.nist.gov/vuln/detail/CVE-2024-35255
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.5
- https://github.com/traefik/traefik/releases/tag/v3.0.3
