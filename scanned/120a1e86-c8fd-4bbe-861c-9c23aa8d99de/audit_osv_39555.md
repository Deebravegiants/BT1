# [C] mptcp: pm: ADD_ADDR rtx: fix potential data-race

## Summary
Severity: Critical
Advisory: CVE-2026-46137
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46137
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.141, >=6.7.0 <6.12.91, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: pm: ADD_ADDR rtx: fix potential data-race

This mptcp_pm_add_timer() helper is executed as a timer callback in
softirq context. To avoid any data races, the socket lock needs to be
held with bh_lock_sock().

If the socket is in use, retry again soon after, similar to what is done
with the keepalive timer.

## References
- https://git.kernel.org/stable/c/013dcdc1961543b9a3433466bc8c79a2f4ca75b5
- https://git.kernel.org/stable/c/23079e0b7742ec114d3507c3e3aad01b7b69e4af
- https://git.kernel.org/stable/c/2ad56e434199ca24a812bb353667aa1c3860f513
- https://git.kernel.org/stable/c/5cd6e0ad79d2615264f63929f8b457ad97ae550d
- https://git.kernel.org/stable/c/6e4710d7d8782cb61af29a7e7111ddfc38b9e1a3
- https://git.kernel.org/stable/c/b35605e1f1e877038c8c9d499babbc891cdd234f
- https://git.kernel.org/stable/c/cc3c0399361efaaf7ae64262eb3f70829b1189c6
- https://git.kernel.org/stable/c/d9b272a85fe6b8f993e37915311e4038c814a533
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46137.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46137
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
