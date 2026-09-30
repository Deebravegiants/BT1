# [C] microtar 0.1.0 Stack-Based Buffer Overflow via raw_to_header()

## Summary
Severity: Critical
Advisory: CVE-2026-43623
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-01
Source: https://osv.dev/vulnerability/CVE-2026-43623
Type: osv

## Details
microtar through 0.1.0 contains a stack-based buffer overflow vulnerability in the raw_to_header() function in src/microtar.c that allows attackers to corrupt adjacent stack memory by supplying a crafted TAR archive with non-null-terminated name or linkname fields. The function uses strcpy() to copy 100-byte ustar format fields that lack null terminators, causing writes of up to 355 bytes into a 100-byte destination buffer when mtar_open(), mtar_find(), or mtar_read_header() process attacker-supplied TAR archives.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43623.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-43623
- https://www.vulncheck.com/advisories/microtar-stack-based-buffer-overflow-via-raw-to-header
- https://github.com/rxi/microtar/issues/28
- https://github.com/rxi/microtar/issues/29
- https://github.com/rxi/microtar/issues/30
- https://github.com/rxi/microtar
