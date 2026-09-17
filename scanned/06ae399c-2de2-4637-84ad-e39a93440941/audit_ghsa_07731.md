# [M] EVE Freely Allocates Buffer on The Stack With Data From Socket

## Summary
Severity: Medium
Advisory: GHSA-6jp5-grgh-jw42
CVE: CVE-2023-43632
CWE: CWE-770, CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H (CVSS_V3)
Published: 2026-02-04
Source: https://github.com/advisories/GHSA-6jp5-grgh-jw42
Type: github-advisory

## Affected
- Go: `github.com/lf-edge/eve` — affected >=0 <0.0.0-20230519072751-977f42b07fa9

## Details
### Impact

VTPM server listens on port 8877, exposing limited TPM functionality. The server reads 4 bytes as a uint32 size header, then allocates that amount on the stack for incoming data. This allows Denial of Service attacks against the vTPM service.

An workload (a container or VM) running on EVE-OS can use this to generate a DOS against the vTPM service.

### Patches

Fixed in 9.4.3-lts and 10.1.0

### Workarounds

None

## References
- https://github.com/lf-edge/eve/security/advisories/GHSA-6jp5-grgh-jw42
- https://nvd.nist.gov/vuln/detail/CVE-2023-43632
- https://asrg.io/security-advisories/cve-2023-43632
- https://asrg.io/security-advisories/freely-allocate-buffer-on-the-stack-with-data-from-socket
- https://github.com/lf-edge/eve
