# [M] Initial debug-host handler implementation could leak information and facilitate denial of service

## Summary
Severity: Medium
Advisory: GHSA-x477-fq37-q5wr
CWE: CWE-200
Ecosystem: Go
Published: 2023-01-27
Source: https://github.com/advisories/GHSA-x477-fq37-q5wr
Type: github-advisory

## Affected
- Go: `fortio.org/proxy` — affected >=1.5.0 <1.6.1

## Details
### Impact
version 1.5.0 and 1.6.0 when using the new `debug-host` feature could expose unnecessary information about the host

### Patches
Use 1.6.1 or newer

### Workarounds
Downgrade to 1.4.0 or set `debug-host` to empty

### References
https://github.com/fortio/proxy/pull/38

Q&A https://github.com/fortio/proxy/discussions

## References
- https://github.com/fortio/proxy/security/advisories/GHSA-x477-fq37-q5wr
- https://github.com/fortio/proxy/pull/38
- https://github.com/fortio/proxy
