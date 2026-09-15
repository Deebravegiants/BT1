# [H] Docker Authentication Bypass

## Summary
Severity: High
Advisory: GHSA-qrqr-3x5j-2xw9
CVE: CVE-2018-12608
CWE: CWE-288
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-qrqr-3x5j-2xw9
Type: github-advisory

## Affected
- Go: `github.com/docker/docker` — affected >=0 <17.06.0-ce

## Details
An issue was discovered in Docker Moby before 17.06.0. The Docker engine validated a client TLS certificate using both the configured client CA root certificate and all system roots on non-Windows systems. This allowed a client with any domain validated certificate signed by a system-trusted root CA (as opposed to one signed by the configured CA root certificate) to authenticate.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-12608
- https://github.com/moby/moby/issues/33173
- https://github.com/moby/moby/pull/33182
- https://github.com/moby/moby/commit/190c6e8cf8b893874a33d83f78307f1bed0bfbcd
- https://github.com/moby/moby
