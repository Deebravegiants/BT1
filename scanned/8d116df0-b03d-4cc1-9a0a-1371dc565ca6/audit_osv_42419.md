# [H] tcp: challenge ACK for non-exact RST in SYN-RECEIVED

## Summary
Severity: High
Advisory: CVE-2026-68118
Ecosystem: Linux
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68118
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.6.0 <6.6.153, >=6.7.0 <6.12.105, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: challenge ACK for non-exact RST in SYN-RECEIVED

The SYN-RECEIVED request-socket path in tcp_check_req() accepts an
in-window RST without requiring SEG.SEQ to exactly match RCV.NXT.  A
non-exact RST therefore removes the request instead of eliciting a
challenge ACK.

RFC 9293 section 3.10.7.4 applies the RFC 5961 reset check in
SYN-RECEIVED: an exact RST resets the connection, while a non-exact
in-window RST must trigger a challenge ACK and be dropped.

Apply that check before the ACK-field validation, following the RFC
sequence-number, RST, then ACK processing order.  Factor the per-netns
challenge ACK quota out of tcp_send_challenge_ack() so request sockets
can share it.  Use the request socket's send_ack() callback and its own
out-of-window ACK timestamp to send and rate-limit the response.

## References
- https://git.kernel.org/stable/c/0fe4636665d14a258de70b4f3e8248e6d42038f1
- https://git.kernel.org/stable/c/22cec809b048495310f206d9abbcdbbfbdce3ae3
- https://git.kernel.org/stable/c/234f9ffbd9b2c1b24ec67200ea3cff07401bec48
- https://git.kernel.org/stable/c/8b0a3a094f4cae2fb92e4d08d4eef7246a9d9c49
- https://git.kernel.org/stable/c/a28c4fcbf774e23b4779cae468e3497a5ad1f4a1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68118.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68118
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
