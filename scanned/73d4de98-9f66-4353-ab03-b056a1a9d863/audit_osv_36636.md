# [M] A potential heap-buffer overflow in praydog/UEVR

## Summary
Severity: Medium
Advisory: CVE-2026-24817
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:L/S:N/AU:Y/R:U/V:D/RE:M/U:Amber)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24817
Type: osv

## Details
Out-of-bounds Write vulnerability in praydog UEVR (dependencies/lua/src modules). This vulnerability is associated with program files ldebug.C, lvm.C.

This issue affects UEVR: before 1.05.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24817.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24817
- https://github.com/praydog/UEVR/pull/336
- https://github.com/praydog/UEVR
