# [C] net: ethernet: cortina: Carry over frag counter

## Summary
Severity: Critical
Advisory: CVE-2026-64055
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64055
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: cortina: Carry over frag counter

The gmac_rx() NAPI poll function assembles packets in an
SKB from a ring buffer.

If the ring buffer gets completely emptied during a poll cycle,
we exit gmac_rx(), but the packet is not yet completely
assembled in the SKB, yet the fragment counter frag_nr is
reset to zero on the next invocation.

Solve this by making the RX fragment counter a part of the
port struct, and carry it over between invocations.

Reset the fragment counter only right after calling
napi_gro_frags(), on error (after calling napi_free_frags())
or if stopping the port.

Reset it in some place where not strictly necessary just to
emphasize what is going on.

This was found by Sashiko during normal patch review.

## References
- https://git.kernel.org/stable/c/46806096f35b8d3dfa2f321ddd77f597edcdb85f
- https://git.kernel.org/stable/c/7123cf481e21b54eb6adc4cb0d8dc2876aeaee41
- https://git.kernel.org/stable/c/75105fcf73f1ce7d9f769aaefec6e6d6645d5ac0
- https://git.kernel.org/stable/c/78cf08b3be47c28f07008a76c932bad7cdffa9d8
- https://git.kernel.org/stable/c/7af1fabdee744b7995fe01b30b77dfc397657cb5
- https://git.kernel.org/stable/c/c373b34877afea61c89e0dd2e38948c624249b9b
- https://git.kernel.org/stable/c/df31e3b64455293df1ea89c7da7d5c9bfbcdd253
- https://git.kernel.org/stable/c/ebd8ec2b309e3a447851b456ccaf8fb39f3661e7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64055.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64055
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
