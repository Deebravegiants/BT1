# [H] can: gw: fix OOB heap access in cgw_csum_crc8_rel()

## Summary
Severity: High
Advisory: CVE-2026-31570
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-24
Source: https://osv.dev/vulnerability/CVE-2026-31570
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.168, >=6.2.0 <6.6.131, >=6.7.0 <6.12.80, >=6.13.0 <6.18.21, >=6.19.0 <6.19.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

can: gw: fix OOB heap access in cgw_csum_crc8_rel()

cgw_csum_crc8_rel() correctly computes bounds-safe indices via calc_idx():

    int from = calc_idx(crc8->from_idx, cf->len);
    int to   = calc_idx(crc8->to_idx,   cf->len);
    int res  = calc_idx(crc8->result_idx, cf->len);

    if (from < 0 || to < 0 || res < 0)
        return;

However, the loop and the result write then use the raw s8 fields directly
instead of the computed variables:

    for (i = crc8->from_idx; ...)        /* BUG: raw negative index */
    cf->data[crc8->result_idx] = ...;    /* BUG: raw negative index */

With from_idx = to_idx = result_idx = -64 on a 64-byte CAN FD frame,
calc_idx(-64, 64) = 0 so the guard passes, but the loop iterates with
i = -64, reading cf->data[-64], and the write goes to cf->data[-64].
This write might end up to 56 (7.0-rc) or 40 (<= 6.19) bytes before the
start of the canfd_frame on the heap.

The companion function cgw_csum_xor_rel() uses `from`/`to`/`res`
correctly throughout; fix cgw_csum_crc8_rel() to match.

Confirmed with KASAN on linux-7.0-rc2:
  BUG: KASAN: slab-out-of-bounds in cgw_csum_crc8_rel+0x515/0x5b0
  Read of size 1 at addr ffff8880076619c8 by task poc_cgw_oob/62

To configure the can-gw crc8 checksums CAP_NET_ADMIN is needed.

## References
- https://git.kernel.org/stable/c/54ecdf76a55e75c1f5085e440f8ab671a3283ef5
- https://git.kernel.org/stable/c/66b689efd08227da2c5ca49b58b30a95d23c695a
- https://git.kernel.org/stable/c/84f8b76d24273175a22713e83e90874e1880d801
- https://git.kernel.org/stable/c/999ca48d55a8a46da21519db7e834e5867200379
- https://git.kernel.org/stable/c/a025283d7f7404c739225e457fb99db2368bb544
- https://git.kernel.org/stable/c/b9c310d72783cc2f30d103eed83920a5a29c671a
- https://git.kernel.org/stable/c/c4e8eaa75fa0b6bcbfa5356d6195c4ad0e05e57a
- https://git.kernel.org/stable/c/e7c99348b0612b2bc02d5ce6ff9873261cc7605f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31570.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31570
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
