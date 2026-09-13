# [M] CVE-2026-55706

## Summary
Severity: Medium
Advisory: CVE-2026-55706
CVSS: 5.8 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:L/I:L/A:L)
Published: 2026-06-17
Source: https://osv.dev/vulnerability/CVE-2026-55706
Type: osv

## Details
sppp_pap_input in sys/net/if_spppsubr.c in OpenBSD before 076e2b1 allows authentication bypass via certain zero values for lengths.

## References
- https://www.openwall.com/lists/oss-security/2026/06/16/9
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55706.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-55706
- https://github.com/openbsd/src/commit/076e2b1c1fc4ac0883a72d3544131ad5cee7adf8
- https://blog.argus-systems.ai/blog/openbsd-pap-27-year-auth-bypass.html
- https://blog.argus-systems.ai/blog/poc-001-pap-bypass.py
