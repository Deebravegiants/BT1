# [C] Stack Buffer Overflow in rxi/microtar raw_to_header() via non-null-terminated TAR name field

## Summary
Severity: Critical
Advisory: CVE-2026-55738
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-55738
Type: osv

## Details
A stack-based buffer overflow exists in the raw_to_header function in src/microtar.c in rxi microtar 0.1.0. The function copies the 100-byte name and linkname fields of a TAR header with strcpy without guaranteeing null termination of the source.

## References
- https://github.com/rxi/microtar/blob/master/src/microtar.c#L111
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55738.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55738
- https://github.com/rxi/microtar
- https://raw.githubusercontent.com/rxi/microtar/master/src/microtar.c
