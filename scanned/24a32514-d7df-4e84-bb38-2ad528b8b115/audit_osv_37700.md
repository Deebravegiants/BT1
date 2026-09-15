# [M] NetBSD cryptodev Race Condition Double-Free via cryptodev_op()

## Summary
Severity: Medium
Advisory: CVE-2026-32848
CVSS: 6.0 (CVSS:4.0/AV:L/AC:H/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-18
Source: https://osv.dev/vulnerability/CVE-2026-32848
Type: osv

## Details
NetBSD prior to commit ec8451e contains a race condition vulnerability in cryptodev_op() within the opencrypto subsystem that allows local attackers to trigger a double-free condition by concurrently issuing CIOCCRYPT operations on the same session identifier on SMP systems. Attackers can exploit mutable per-operation state embedded in the csession struct to corrupt kernel heap memory.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/32xxx/CVE-2026-32848.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-32848
- https://www.vulncheck.com/advisories/netbsd-cryptodev-race-condition-double-free-via-cryptodev-op
- https://github.com/NetBSD/src/commit/ec8451efc1565516aba9e7047e1a1a1ce7953a2f
- https://github.com/NetBSD/src
- https://nasm.re/posts/uaf_netbsd_crypto/
