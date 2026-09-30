# [H] mptcp: cope racing subflow creation in mptcp_rcv_space_adjust

## Summary
Severity: High
Advisory: CVE-2024-53122
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-02
Source: https://osv.dev/vulnerability/CVE-2024-53122
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.0 <5.15.174, >=5.16.0 <6.1.119, >=6.2.0 <6.6.63, >=6.7.0 <6.11.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

mptcp: cope racing subflow creation in mptcp_rcv_space_adjust

Additional active subflows - i.e. created by the in kernel path
manager - are included into the subflow list before starting the
3whs.

A racing recvmsg() spooling data received on an already established
subflow would unconditionally call tcp_cleanup_rbuf() on all the
current subflows, potentially hitting a divide by zero error on
the newly created ones.

Explicitly check that the subflow is in a suitable state before
invoking tcp_cleanup_rbuf().

## References
- https://git.kernel.org/stable/c/0a9a182ea5c7bb0374e527130fd85024ace7279b
- https://git.kernel.org/stable/c/24995851d58c4a205ad0ffa7b2f21e479a9c8527
- https://git.kernel.org/stable/c/aad6412c63baa39dd813e81f16a14d976b3de2e8
- https://git.kernel.org/stable/c/ce7356ae35943cc6494cc692e62d51a734062b7d
- https://git.kernel.org/stable/c/ff825ab2f455299c0c7287550915a8878e2a66e0
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53122.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53122
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
