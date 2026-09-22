# [H] xfrm: Check for underflow in xfrm_state_mtu

## Summary
Severity: High
Advisory: CVE-2026-64009
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64009
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.22 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=6.2.0 <6.6.143, >=6.7.0 <6.12.93, >=6.13.0 <6.18.35, >=6.19.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: Check for underflow in xfrm_state_mtu

Leo Lin reported OOB write issue in esp component:

  xfrm_state_mtu() returns u32 but performs its arithmetic in unsigned
  modulo-2^32 space using an attacker-influenced "header_len + authsize +
  net_adj" subtracted from a small "mtu" argument. A nobody user can
  install an IPv4 ESP tunnel SA with a large authentication key
  (XFRMA_ALG_AUTH_TRUNC, e.g. hmac(sha512), 64-byte key, 64-byte trunc),
  configure a small interface MTU (68 bytes), and set XFRMA_TFCPAD to a
  large value. When a single UDP datagram is then sent through the
  tunnel, xfrm_state_mtu() underflows to a near-2^32 value, and
  esp_output() consumes it as a signed int via:

        padto      = min(x->tfcpad, xfrm_state_mtu(x, mtu_cached))
        esp.tfclen = padto - skb->len   (assigned to int)

  esp.tfclen ends up negative (e.g. -207). It is sign-extended to size_t
  when passed to memset() inside esp_output_fill_trailer(), producing a
  ~16 EB write of zeroes at skb_tail_pointer(skb). KASAN logs it as
  "Write of size 18446744073709551537 at addr ffff888...".

Check for underflow and return 1. This causes the sendmsg attempt to
fail with ENETUNREACH.

## References
- https://git.kernel.org/stable/c/1021d2877b689a648b27815c854557a917122e93
- https://git.kernel.org/stable/c/2a41b1b31c61c52b972278ce1732a1443f5e89ed
- https://git.kernel.org/stable/c/3db50ceeacb52806d8fe86fb1dfe944df0b9f789
- https://git.kernel.org/stable/c/742b04d0550b0ec89dcbc99537ec88653bd1ad90
- https://git.kernel.org/stable/c/8014f70c4e6e5ab101ae3860a614e65e988372e3
- https://git.kernel.org/stable/c/820e501be8aee4b365d218d83227b314309c5fda
- https://git.kernel.org/stable/c/82ac903e0b519849647657b8c48d21237ada06a2
- https://git.kernel.org/stable/c/fccd685b32df5aaf6bad4381eeda216468e283f0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64009.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64009
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
