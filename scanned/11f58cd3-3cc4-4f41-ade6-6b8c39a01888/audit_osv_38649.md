# [M] Unauthenticated Go pprof exposure in Calico debug server

## Summary
Severity: Medium
Advisory: CVE-2026-41186
CVSS: 6.0 (CVSS:4.0/AV:A/AC:L/AT:P/PR:N/UI:N/VC:H/VI:N/VA:N/SC:L/SI:L/SA:L)
Published: 2026-07-30
Source: https://osv.dev/vulnerability/CVE-2026-41186
Type: osv

## Details
When Calico's shared debug server is enabled (disabled by default), the Calico kube-controllers and Goldmane components bind their Go pprof debug listener to 0.0.0.0 without authentication. Any pod with network reachability to the listener can retrieve the process heap, goroutine stacks (including function arguments), and command-line arguments. Depending on the process's in-memory state, the heap may contain sensitive material. The debug listener is opt-in but is unsafe when enabled because it offers no authentication and no safe localhost-only binding option.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41186.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41186
- https://www.tigera.io/security-bulletins/tta-2026-004/
- https://github.com/projectcalico/calico/pull/12491
- https://github.com/projectcalico/calico/pull/12633
- https://github.com/projectcalico/calico/pull/12634
