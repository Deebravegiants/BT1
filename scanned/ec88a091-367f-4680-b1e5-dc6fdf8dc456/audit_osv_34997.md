# [H] CVE-2025-67269

## Summary
Severity: High
Advisory: CVE-2025-67269
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-01-02
Source: https://osv.dev/vulnerability/CVE-2025-67269
Type: osv

## Details
An integer underflow vulnerability exists in the `nextstate()` function in `gpsd/packet.c` of gpsd versions prior to commit `ffa1d6f40bca0b035fc7f5e563160ebb67199da7`. When parsing a NAVCOM packet, the payload length is calculated using `lexer->length = (size_t)c - 4` without checking if the input byte `c` is less than 4. This results in an unsigned integer underflow, setting `lexer->length` to a very large value (near `SIZE_MAX`). The parser then enters a loop attempting to consume this massive number of bytes, causing 100% CPU utilization and a Denial of Service (DoS) condition.

## References
- https://github.com/Jaenact/gspd_cve/blob/main/CVE-2025-67269/README.md
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-67269.json
- https://access.redhat.com/errata/RHSA-2026:0770
- https://access.redhat.com/errata/RHSA-2026:0771
- https://access.redhat.com/security/cve/CVE-2025-67269
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67269.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67269
- https://bugzilla.redhat.com/show_bug.cgi?id=2426810
- https://gitlab.com/gpsd/gpsd/-/commit/ffa1d6f40bca0b035fc7f5e563160ebb67199da7
- https://gitlab.com/gpsd/gpsd
