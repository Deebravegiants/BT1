# [C] net: tls: fix off-by-one in sg_chain entry count for wrapped sk_msg ring

## Summary
Severity: Critical
Advisory: CVE-2026-64047
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64047
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.5.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: tls: fix off-by-one in sg_chain entry count for wrapped sk_msg ring

When an sk_msg scatterlist ring wraps (sg.end < sg.start),
tls_push_record() chains the tail portion of the ring to the head
using sg_chain(). An extra entry in the sg array is reserved for
this:

  struct sk_msg_sg {
        [...]
        /* The extra two elements:
         * 1) used for chaining the front and sections when the list becomes
         *    partitioned (e.g. end < start). The crypto APIs require the
         *    chaining;
         * 2) to chain tailer SG entries after the message.
         */
        struct scatterlist              data[MAX_MSG_FRAGS + 2];

The current code uses MAX_SKB_FRAGS + 1 as the ring size:

    sg_chain(&msg_pl->sg.data[msg_pl->sg.start],
             MAX_SKB_FRAGS - msg_pl->sg.start + 1,
             msg_pl->sg.data);

This places the chain pointer at

  sg_chain(data[start], (MAX_SKB_FRAGS - msg_start + 1) .. =
  &data[start] + (MAX_SKB_FRAGS - msg_start + 1) - 1 =
  data[start + (MAX_SKB_FRAGS - start + 1) - 1] =
  data[MAX_SKB_FRAGS]

instead of the true last entry. This is likely due to a "race" of
the commit under Fixes landing close to
commit 031097d9e079 ("bpf: sk_msg, zap ingress queue on psock down")

Convert to ARRAY_SIZE and drop the data[start] / - start (as suggested
by Sabrina).

## References
- https://git.kernel.org/stable/c/131ef12057d92b77b636321b7849c69222405a97
- https://git.kernel.org/stable/c/285943c6e7ca309bbea84b253745154241d9788a
- https://git.kernel.org/stable/c/2fb0dc7e0099686c4e9d2732745d8a31b18c3628
- https://git.kernel.org/stable/c/47110c3a9ac247b688657337f5981efcfcb240dc
- https://git.kernel.org/stable/c/66339b71f105e6f83e0da3b9583d95077534fe1d
- https://git.kernel.org/stable/c/73963a375885d5ccb7def39fd0b4f542e0f343dd
- https://git.kernel.org/stable/c/84158c2997159df4a0d70cd9c46774512d32a522
- https://git.kernel.org/stable/c/eca989eab4b2599dcb02f72140a7c08f08838520
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64047.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64047
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
