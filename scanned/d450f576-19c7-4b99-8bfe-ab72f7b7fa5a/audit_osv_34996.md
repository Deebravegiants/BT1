# [C] CVE-2025-67268

## Summary
Severity: Critical
Advisory: CVE-2025-67268
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-02
Source: https://osv.dev/vulnerability/CVE-2025-67268
Type: osv

## Details
gpsd before commit dc966aa contains a heap-based out-of-bounds write vulnerability in the drivers/driver_nmea2000.c file. The hnd_129540 function, which handles NMEA2000 PGN 129540 (GNSS Satellites in View) packets, fails to validate the user-supplied satellite count against the size of the skyview array (184 elements). This allows an attacker to write beyond the bounds of the array by providing a satellite count up to 255, leading to memory corruption, Denial of Service (DoS), and potentially arbitrary code execution.

## References
- https://github.com/Jaenact/gspd_cve/blob/main/CVE-2025-67268/README.md
- https://github.com/ntpsec/gpsd/blob/master/drivers/driver_nmea2000.c
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-67268.json
- https://access.redhat.com/errata/RHSA-2026:0770
- https://access.redhat.com/errata/RHSA-2026:0771
- https://access.redhat.com/errata/RHSA-2026:1621
- https://access.redhat.com/security/cve/CVE-2025-67268
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/67xxx/CVE-2025-67268.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-67268
- https://bugzilla.redhat.com/show_bug.cgi?id=2426835
- https://github.com/ntpsec/gpsd/commit/dc966aa74c075d0a6535811d98628625cbfbe3f4
