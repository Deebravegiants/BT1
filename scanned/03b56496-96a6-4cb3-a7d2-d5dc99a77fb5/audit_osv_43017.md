# [H] net/tls: Consume empty data records in tls_sw_read_sock()

## Summary
Severity: High
Advisory: CVE-2026-72330
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72330
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net/tls: Consume empty data records in tls_sw_read_sock()

A peer may send a zero-length TLS application_data record; TLS 1.3
explicitly permits these as a traffic-analysis countermeasure (RFC
8446, Section 5.1). After decryption such a record has full_len ==
0. tls_sw_read_sock() hands it to the read_actor, which has no
payload to consume and returns zero. The loop treats a zero return
as backpressure (used <= 0), requeues the skb at the head of
rx_list, and stops. rx_list is serviced head-first on the next
call, so the empty record is dequeued, fails the same way, and is
requeued again; every later record on the connection is blocked
behind it.

tls_sw_recvmsg() does not stall on this: a zero-length data record
copies nothing and falls through to consume_skb(). Mirror that in
the read_sock() path by recognizing an empty data record before
the actor runs, consuming it, and continuing.

## References
- https://git.kernel.org/stable/c/0867b0f2513ebc1c475af9898c97f4772a68d964
- https://git.kernel.org/stable/c/3be28e2c9cd0230cb51fd4967df095273afd3848
- https://git.kernel.org/stable/c/c6b440cf766a557b08d25f1b571b3d57d039686e
- https://git.kernel.org/stable/c/e8a4c9fc437b16aef38f86ce3275677e36924259
- https://git.kernel.org/stable/c/ebc295ce343600c2d60c1e1e0c5d192080217457
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72330.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72330
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
