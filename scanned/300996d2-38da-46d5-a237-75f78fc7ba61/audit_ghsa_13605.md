# [M] Traefik vulnerable to HTTP/2 request causing denial of service 

## Summary
Severity: Medium
Advisory: GHSA-7v4p-328v-8v5g
CWE: CWE-400
Ecosystem: Go
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-7v4p-328v-8v5g
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik` — affected >=0 <2.10.5
- Go: `github.com/traefik/traefik` — affected >=3.0.0-beta1 <3.0.0-beta4

## Details
### Impact

A vulnerability CVE-2023-39325 exists in [Go managing HTTP/2 requests](https://groups.google.com/g/golang-announce/c/iNNxDTCjZvo/m/UDd7VKQuAAAJ?pli=1), which impacts Traefik. This vulnerability could be exploited to cause a denial of service.

### References

- [CVE-2023-44487](https://www.cve.org/CVERecord?id=CVE-2023-44487)
- [CVE-2023-39325](https://www.cve.org/CVERecord?id=CVE-2023-39325)

### Patches

- https://github.com/traefik/traefik/releases/tag/v2.10.5
- https://github.com/traefik/traefik/releases/tag/v3.0.0-beta4

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-7v4p-328v-8v5g
- https://github.com/traefik/traefik
- https://groups.google.com/g/golang-announce/c/iNNxDTCjZvo/m/UDd7VKQuAAAJ?pli=1
