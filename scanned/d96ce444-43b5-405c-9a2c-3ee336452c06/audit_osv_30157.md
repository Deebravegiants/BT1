# [H] Bluetooth: SCO: Fix UAF on sco_sock_timeout

## Summary
Severity: High
Advisory: CVE-2024-50125
Ecosystem: Linux
CVSS: 8.0 (CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-05
Source: https://osv.dev/vulnerability/CVE-2024-50125
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.265, >=5.11.0 <5.15.181, >=5.15.0 <6.1.115, >=5.16.0 <6.6.59, >=6.2.0 <6.11.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: SCO: Fix UAF on sco_sock_timeout

conn->sk maybe have been unlinked/freed while waiting for sco_conn_lock
so this checks if the conn->sk is still valid by checking if it part of
sco_sk_list.

## References
- https://git.kernel.org/stable/c/1bf4470a3939c678fb822073e9ea77a0560bc6bb
- https://git.kernel.org/stable/c/678386459ffc07d2fbfbfe33456013786975cfef
- https://git.kernel.org/stable/c/74a466a15731a754bcd8b5a83c126b5122e15a45
- https://git.kernel.org/stable/c/80b05fbfa998480fb3d5299d93eab946f51e9c36
- https://git.kernel.org/stable/c/9ddda5d967e84796e7df1b54a55f36b4b9f21079
- https://git.kernel.org/stable/c/d30803f6a972b5b9e26d1d43b583c7ec151de04b
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50125.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50125
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
