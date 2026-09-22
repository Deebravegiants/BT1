# [H] tcp: avoid too many retransmit packets

## Summary
Severity: High
Advisory: CVE-2024-41007
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-15
Source: https://osv.dev/vulnerability/CVE-2024-41007
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.19.0 <4.19.318, >=4.20.0 <5.4.280, >=5.5.0 <5.10.222, >=5.11.0 <5.15.163, >=5.16.0 <6.1.100, >=6.2.0 <6.6.41, >=6.7.0 <6.9.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: avoid too many retransmit packets

If a TCP socket is using TCP_USER_TIMEOUT, and the other peer
retracted its window to zero, tcp_retransmit_timer() can
retransmit a packet every two jiffies (2 ms for HZ=1000),
for about 4 minutes after TCP_USER_TIMEOUT has 'expired'.

The fix is to make sure tcp_rtx_probe0_timed_out() takes
icsk->icsk_user_timeout into account.

Before blamed commit, the socket would not timeout after
icsk->icsk_user_timeout, but would use standard exponential
backoff for the retransmits.

Also worth noting that before commit e89688e3e978 ("net: tcp:
fix unexcepted socket die when snd_wnd is 0"), the issue
would last 2 minutes instead of 4.

## References
- https://git.kernel.org/stable/c/04317a2471c2f637b4c49cbd0e9c0d04a519f570
- https://git.kernel.org/stable/c/5d7e64d70a11d988553a08239c810a658e841982
- https://git.kernel.org/stable/c/66cb64a1d2239cd0309f9b5038b05462570a5be1
- https://git.kernel.org/stable/c/7bb7670f92bfbd05fc41a8f9a8f358b7ffed65f4
- https://git.kernel.org/stable/c/97a9063518f198ec0adb2ecb89789de342bb8283
- https://git.kernel.org/stable/c/d2346fca5bed130dc712f276ac63450201d52969
- https://git.kernel.org/stable/c/dfcdd7f89e401d2c6616be90c76c2fac3fa98fde
- https://git.kernel.org/stable/c/e113cddefa27bbf5a79f72387b8fbd432a61a466
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41007.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-41007
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
