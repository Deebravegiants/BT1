# [H] Traefik HTTP header parsing could cause a denial of service 

## Summary
Severity: High
Advisory: GHSA-7hj9-rv74-5g92
CVE: CVE-2023-29013
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-04-11
Source: https://github.com/advisories/GHSA-7hj9-rv74-5g92
Type: github-advisory

## Affected
- Go: `github.com/traefik/traefik/v2` — affected >=0 <2.9.10
- Go: `github.com/traefik/traefik/v2` — affected >=2.10.0-rc1 <2.10.0-rc2

## Details
### Impact

There is a vulnerability in [Go when parsing the HTTP headers](https://groups.google.com/g/golang-announce/c/Xdv6JL9ENs8/m/OV40vnafAwAJ), which impacts Traefik.
HTTP header parsing could allocate substantially more memory than required to hold the parsed headers. This behavior could be exploited to cause a denial of service.

### References

- [CVE-2023-24534](https://www.cve.org/CVERecord?id=CVE-2023-24534)

### Patches
- https://github.com/traefik/traefik/releases/tag/v2.9.10
- https://github.com/traefik/traefik/releases/tag/v2.10.0-rc2

### Workarounds

No workaround.

### For more information

If you have any questions or comments about this advisory, please [open an issue](https://github.com/traefik/traefik/issues).

## References
- https://github.com/traefik/traefik/security/advisories/GHSA-7hj9-rv74-5g92
- https://nvd.nist.gov/vuln/detail/CVE-2023-29013
- https://github.com/traefik/traefik/commit/4ed3964b3586565519249bbdc55eb1b961c08c49
- https://github.com/advisories/GHSA-8v5j-pwr7-w5f8
- https://github.com/traefik/traefik
- https://github.com/traefik/traefik/releases/tag/v2.10.0-rc2
- https://github.com/traefik/traefik/releases/tag/v2.9.10
- https://groups.google.com/g/golang-announce/c/Xdv6JL9ENs8/m/OV40vnafAwAJ
- https://security.netapp.com/advisory/ntap-20230517-0008
