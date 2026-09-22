# [M] free5GC SMF crash (nil pointer dereference) on PFCP SessionReportRequest when ReportType.USAR=1 and UsageReport omits mandatory URRID sub-IE ￼

## Summary
Severity: Medium
Advisory: CVE-2026-26024
Aliases: GHSA-mrv4-m9wc-c4g9
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N/E:U)
Published: 2026-02-24
Source: https://osv.dev/vulnerability/CVE-2026-26024
Type: osv

## Details
free5GC SMF provides Session Management Function for free5GC, an open-source project for 5th generation (5G) mobile core networks. In versions up to and including 1.4.1, SMF panics and terminates when processing a malformed PFCP SessionReportRequest on the PFCP (UDP/8805) interface. ￼No known upstream fix is available, but some workarounds are available. ACL/firewall the PFCP interface so only trusted UPF IPs can reach SMF (reduce spoofing/abuse surface); drop/inspect malformed PFCP SessionReportRequest messages at the network edge where feasible, and/or add recover() around PFCP handler dispatch to avoid whole-process termination (mitigation only).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/26xxx/CVE-2026-26024.json
- https://github.com/free5gc/free5gc/security/advisories/GHSA-mrv4-m9wc-c4g9
- https://nvd.nist.gov/vuln/detail/CVE-2026-26024
- https://github.com/free5gc/free5gc/issues/807
