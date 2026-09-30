# [H] scsi: iscsi_tcp: Fix UAF during login when accessing the shost ipaddress

## Summary
Severity: High
Advisory: CVE-2023-52974
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-27
Source: https://osv.dev/vulnerability/CVE-2023-52974
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.39 <4.14.306, >=4.15.0 <4.19.273, >=4.20.0 <5.4.232, >=5.5.0 <5.10.168, >=5.11.0 <5.15.93, >=5.16.0 <6.1.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

scsi: iscsi_tcp: Fix UAF during login when accessing the shost ipaddress

If during iscsi_sw_tcp_session_create() iscsi_tcp_r2tpool_alloc() fails,
userspace could be accessing the host's ipaddress attr. If we then free the
session via iscsi_session_teardown() while userspace is still accessing the
session we will hit a use after free bug.

Set the tcp_sw_host->session after we have completed session creation and
can no longer fail.

## References
- https://git.kernel.org/stable/c/0aaabdb900c7415caa2006ef580322f7eac5f6b6
- https://git.kernel.org/stable/c/496af9d3682ed4c28fb734342a09e6cc0c056ea4
- https://git.kernel.org/stable/c/61e43ebfd243bcbad11be26bd921723027b77441
- https://git.kernel.org/stable/c/6abd4698f4c8a78e7bbfc421205c060c199554a0
- https://git.kernel.org/stable/c/9758ffe1c07b86aefd7ca8e40d9a461293427ca0
- https://git.kernel.org/stable/c/d4d765f4761f9e3a2d62992f825aeee593bcb6b9
- https://git.kernel.org/stable/c/f484a794e4ee2a9ce61f52a78e810ac45f3fe3b3
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52974.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52974
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
