# [M] moby docker daemon crash during image pull of malicious image

## Summary
Severity: Medium
Advisory: GHSA-6fj5-m822-rqx8
CVE: CVE-2021-21285
CWE: CWE-400, CWE-754
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-6fj5-m822-rqx8
Type: github-advisory

## Affected
- Go: `github.com/moby/moby` — affected >=0 <19.3.15
- Go: `github.com/moby/moby` — affected >=20.10.0-beta1 <20.10.3

## Details
### Impact

Pulling an intentionally malformed Docker image manifest crashes the `dockerd` daemon.

### Patches

Versions 20.10.3 and 19.03.15 contain patches that prevent the daemon from crashing.

### Credits

Maintainers would like to thank Josh Larsen, Ian Coldwater, Duffie Cooley, Rory McCune for working on the vulnerability and Brad Geesaman for responsibly disclosing it to security@docker.com.

## References
- https://github.com/moby/moby/security/advisories/GHSA-6fj5-m822-rqx8
- https://nvd.nist.gov/vuln/detail/CVE-2021-21285
- https://github.com/moby/moby/commit/8d3179546e79065adefa67cc697c09d0ab137d30
- https://docs.docker.com/engine/release-notes/#20103
- https://github.com/moby/moby/releases/tag/v19.03.15
- https://github.com/moby/moby/releases/tag/v20.10.3
- https://security.gentoo.org/glsa/202107-23
- https://security.netapp.com/advisory/ntap-20210226-0005
- https://www.debian.org/security/2021/dsa-4865
