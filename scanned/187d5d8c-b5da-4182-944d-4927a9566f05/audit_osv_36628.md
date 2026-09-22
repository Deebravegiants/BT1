# [M] Mishandles certain out-of-memory conditions in visualfc/liteide via liteidex/src/3rdparty/libvterm/src module

## Summary
Severity: Medium
Advisory: CVE-2026-24805
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/S:N/AU:N/R:U/V:D/RE:L/U:Amber)
Published: 2026-01-27
Source: https://osv.dev/vulnerability/CVE-2026-24805
Type: osv

## Details
NULL Pointer Dereference vulnerability in visualfc liteide (liteidex/src/3rdparty/libvterm/src modules). This vulnerability is associated with program files screen.C, state.C, vterm.C.

This issue affects liteide: before x38.4.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24805.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-24805
- https://github.com/visualfc/liteide/pull/1326
- https://github.com/visualfc/liteide
