# [C] BuildKit vulnerable to possible host system access from mount stub cleaner

## Summary
Severity: Critical
Advisory: GHSA-4v98-7qmw-rqr8
CVE: CVE-2024-23652
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:H (CVSS_V3)
Published: 2024-01-31
Source: https://github.com/advisories/GHSA-4v98-7qmw-rqr8
Type: github-advisory

## Affected
- Go: `github.com/moby/buildkit` — affected >=0 <0.12.5

## Details
### Impact
A malicious BuildKit frontend or Dockerfile using `RUN --mount` could trick the feature that removes empty files created for the mountpoints into removing a file outside the container, from the host system.

### Patches
The issue has been fixed in v0.12.5

### Workarounds
Avoid using BuildKit frontend from an untrusted source or building an untrusted Dockerfile containing `RUN --mount` feature.

### References

## References
- https://github.com/moby/buildkit/security/advisories/GHSA-4v98-7qmw-rqr8
- https://nvd.nist.gov/vuln/detail/CVE-2024-23652
- https://github.com/moby/buildkit/pull/4603
- https://github.com/moby/buildkit
- https://github.com/moby/buildkit/releases/tag/v0.12.5
