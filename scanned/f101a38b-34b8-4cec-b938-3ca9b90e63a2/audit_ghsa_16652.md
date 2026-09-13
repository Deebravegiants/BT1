# [M] Traefik vulnerable to GO issue allowing malformed DNS message to cause infinite loop

## Summary
Severity: Medium
Advisory: GHSA-f7cq-5v43-8pwp
CWE: CWE-1395
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2024-05-23
Source: https://github.com/advisories/GHSA-f7cq-5v43-8pwp
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.11.3
- Go: `github.com/traefik/traefik/v3` — affected >=0 <3.0.1
- Go: `github.com/traefik/traefik` — affected >=0

## Details
### Impact

There is a vulnerability in [GO managing malformed DNS message](https://groups.google.com/g/golang-announce/c/wkkO4P9stm0), which impacts Traefik.
This vulnerability could be exploited to cause a denial of service.

### References

- [CVE-2024-24788](https://www.cve.org/CVERecord?id=CVE-2024-24788)

### Patches

- https://github.com/traefik/traefik/releases/tag/v2.11.3
- https://github.com/traefik/traefik/releases/tag/v3.0.1

### Workarounds

No workaround.

### For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-f7cq-5v43-8pwp
- https://github.com/advisories/GHSA-5fq7-4mxc-535h
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.11.3
- https://github.com/traefik/traefik/releases/tag/v3.0.1
- https://www.cve.org/CVERecord?id=CVE-2024-24788
