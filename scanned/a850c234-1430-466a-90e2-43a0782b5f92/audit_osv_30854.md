# [C] can: j1939: j1939_session_new(): fix skb reference counting

## Summary
Severity: Critical
Advisory: CVE-2024-56645
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-27
Source: https://osv.dev/vulnerability/CVE-2024-56645
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.66, >=6.7.0 <6.12.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: j1939: j1939_session_new(): fix skb reference counting

Since j1939_session_skb_queue() does an extra skb_get() for each new
skb, do the same for the initial one in j1939_session_new() to avoid
refcount underflow.

[mkl: clean up commit message]

## References
- https://git.kernel.org/stable/c/224e606a8d8e8c7db94036272c47a37455667313
- https://git.kernel.org/stable/c/4199dd78a59896e091d3a7a05a77451aa7fd724d
- https://git.kernel.org/stable/c/426d94815e12b6bdb9a75af294fbbafb9301601d
- https://git.kernel.org/stable/c/68fceb143b635cdc59fed3896d5910aff38f345e
- https://git.kernel.org/stable/c/a8c695005bfe6569acd73d777ca298ddddd66105
- https://git.kernel.org/stable/c/b3282c2bebeeb82ceec492ee4972f51ee7a4a132
- https://git.kernel.org/stable/c/f117cba69cbbd496babb3defcdf440df4fd6fe14
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56645.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56645
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
