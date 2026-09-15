# [C] Tugtainer has RCE in Agent Command Execution Api

## Summary
Severity: Critical
Advisory: CVE-2025-69201
Aliases: GHSA-grc3-8w5x-g54q
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2025-12-29
Source: https://osv.dev/vulnerability/CVE-2025-69201
Type: osv

## Details
Tugtainer is a self-hosted app for automating updates of docker containers. In versions prior to 1.15.1, arbitary arguments can be injected in tugtainer-agent `POST api/command/run`. Version 1.15.1 fixes the issue.

## References
- https://github.com/Quenary/tugtainer/releases/tag/v1.15.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/69xxx/CVE-2025-69201.json
- https://github.com/Quenary/tugtainer/security/advisories/GHSA-grc3-8w5x-g54q
- https://nvd.nist.gov/vuln/detail/CVE-2025-69201
- https://github.com/Quenary/tugtainer/commit/dbb17d843e30fd7509acf0328c913dcb42f40831
- https://github.com/Quenary/tugtainer/pull/88
