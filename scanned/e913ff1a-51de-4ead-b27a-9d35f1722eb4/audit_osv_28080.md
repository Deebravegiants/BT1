# [H] mptcp: fix data races on remote_id

## Summary
Severity: High
Advisory: CVE-2024-27404
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-27404
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.81, >=6.2.0 <6.6.19, >=6.7.0 <6.7.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: fix data races on remote_id

Similar to the previous patch, address the data race on
remote_id, adding the suitable ONCE annotations.

## References
- https://git.kernel.org/stable/c/2dba5774e8ed326a78ad4339d921a4291281ea6e
- https://git.kernel.org/stable/c/967d3c27127e71a10ff5c083583a038606431b61
- https://git.kernel.org/stable/c/987c3ed7297e5661bc7f448f06fc366e497ac9b2
- https://git.kernel.org/stable/c/e64148635509bf13eea851986f5a0b150e5bd066
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27404.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-27404
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
