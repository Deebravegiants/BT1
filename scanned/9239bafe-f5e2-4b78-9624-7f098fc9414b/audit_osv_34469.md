# [M] CVE-2025-60473

## Summary
Severity: Medium
Advisory: CVE-2025-60473
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-06-24
Source: https://osv.dev/vulnerability/CVE-2025-60473
Type: osv

## Details
A NULL pointer dereference in the gf_filter_in_parent_chain function (/filter_core/filter_pid.c) of GPAC Project/MP4Box before 26.02.0 allows attackers to cause a Denial of Service (DoS) via supplying a crafted file.

## References
- http://www.openwall.com/lists/oss-security/2026/06/27/3
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/36/36_gf_filter_in_parent_chain_filter_core_filter_pid_c_2145
- https://github.com/sigdevel/pocs/blob/main/res/gpac/MP4Box/36/README.md
- https://infosec.exchange/@sigdevel/116780471059317580
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/60xxx/CVE-2025-60473.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-60473
- https://github.com/gpac/gpac/issues/3285
- https://github.com/gpac/gpac/commit/b8d80b44718de10b101e1d7fc17c84d69feb092e
