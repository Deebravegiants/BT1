# [H] net: wwan: iosm: bound device offsets in the MUX downlink decoder

## Summary
Severity: High
Advisory: CVE-2026-72029
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-72029
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: wwan: iosm: bound device offsets in the MUX downlink decoder

mux_dl_adb_decode() walks a chain of aggregated datagram tables using
offsets and lengths taken from the modem. first_table_index,
next_table_index, table_length, datagram_index and datagram_length are
all device supplied le values. Only first_table_index was checked, and
only for being non zero. The decoder then formed adth = block +
adth_index and read the table header and the datagram entries with no
bound against the received skb. A modem that reports an index or a
length past the downlink buffer makes the decoder read out of bounds.

The buffer is IPC_MEM_MAX_DL_MUX_LITE_BUF_SIZE and skb->len is at most
that, so skb->len is the real limit, but none of these in band offsets
were checked against it.

The table chain is also followed with no forward progress check. The loop
takes the next table from adth->next_table_index and stops only when that
reaches zero. A modem can stage two tables that point at each other, so
the loop never ends. It runs in softirq and clones the skb on every pass.

Validate every device offset and length against skb->len before use.
The block header must fit. Each table header, on entry and after every
next_table_index, must lie inside the skb. The datagram table must fit.
Each datagram index and length must stay inside the skb. The header
padding must not exceed the datagram length so the receive length does
not wrap. Require each next_table_index to move forward so the chain
cannot cycle.

This was reproduced under KASAN as a slab out of bounds read on a normal
downlink receive once the iosm net device is up.

## References
- https://git.kernel.org/stable/c/07f5eb6d268a37bd9e131079489655cd599182e0
- https://git.kernel.org/stable/c/155851e501d6c649cbcfcca6472dc26269b04b6b
- https://git.kernel.org/stable/c/2b822df8e498aa6ca828e16afd8ffec27f7e4c88
- https://git.kernel.org/stable/c/526b8ef54668780c8f69e0211c342763d5dcbad1
- https://git.kernel.org/stable/c/55cfea8e8d9117ad086d1e1a0ff87f306f8e3ad0
- https://git.kernel.org/stable/c/77f0023f22f6a2616ae128e9c93961b24ae52611
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/72xxx/CVE-2026-72029.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-72029
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
