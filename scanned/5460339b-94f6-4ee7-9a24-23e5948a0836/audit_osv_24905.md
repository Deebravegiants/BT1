# [H] CVE-2023-28339

## Summary
Severity: High
Advisory: CVE-2023-28339
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-14
Source: https://osv.dev/vulnerability/CVE-2023-28339
Type: osv

## Details
OpenDoas through 6.8.2, when TIOCSTI is available, allows privilege escalation because of sharing a terminal with the original session. NOTE: TIOCSTI is unavailable in OpenBSD 6.0 and later, and can be made unavailable in the Linux kernel 6.2 and later.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28339.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28339
- https://github.com/Duncaen/OpenDoas/issues/106
