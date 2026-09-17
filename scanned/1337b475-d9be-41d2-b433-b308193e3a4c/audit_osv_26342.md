# [H] net: can: j1939: enhanced error handling for tightly received RTS messages in xtp_rx_rts_session_new

## Summary
Severity: High
Advisory: CVE-2023-52887
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2023-52887
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.97, >=6.2.0 <6.6.37, >=6.7.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: can: j1939: enhanced error handling for tightly received RTS messages in xtp_rx_rts_session_new

This patch enhances error handling in scenarios with RTS (Request to
Send) messages arriving closely. It replaces the less informative WARN_ON_ONCE
backtraces with a new error handling method. This provides clearer error
messages and allows for the early termination of problematic sessions.
Previously, sessions were only released at the end of j1939_xtp_rx_rts().

Potentially this could be reproduced with something like:
testj1939 -r vcan0:0x80 &
while true; do
	# send first RTS
	cansend vcan0 18EC8090#1014000303002301;
	# send second RTS
	cansend vcan0 18EC8090#1014000303002301;
	# send abort
	cansend vcan0 18EC8090#ff00000000002301;
done

## References
- https://git.kernel.org/stable/c/0bc0a7416ea73f79f915c9a05ac0858dff65cfed
- https://git.kernel.org/stable/c/1762ca80c2b72dd1b5821c5e347713ae696276ea
- https://git.kernel.org/stable/c/177e33b655d35d72866b50aec84307119dc5f3d4
- https://git.kernel.org/stable/c/26b18dd30e63d4fd777be429148e8e4ed66f60b2
- https://git.kernel.org/stable/c/d3e2904f71ea0fe7eaff1d68a2b0363c888ea0fb
- https://git.kernel.org/stable/c/ed581989d7ea9df6f8646beba2341e32cd49a1f9
- https://git.kernel.org/stable/c/f6c839e717901dbd6b1c1ca807b6210222eb70f6
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/52xxx/CVE-2023-52887.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-52887
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
