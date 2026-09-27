# [C] net: ethernet: cortina: Make RX SKB per-port

## Summary
Severity: Critical
Advisory: CVE-2026-64056
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-64056
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.16.0 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.142, >=6.7.0 <6.12.92, >=6.13.0 <6.18.34, >=6.19.0 <7.0.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

net: ethernet: cortina: Make RX SKB per-port

The SKB used to assemble packets from fragments in gmac_rx()
is static local, but the Gemini has two ethernet ports, meaning
there can be races between the ports on a bad day if a device
is using both.

Make the RX SKB a per-port variable and carry it over between
invocations in the port struct instead.

Zero the pointer once we call napi_gro_frags(), on error (after
calling napi_free_frags()) or if the port is stopped.

Zero it in some place where not strictly necessary just to
emphasize what is going on.

This was found by Sashiko during normal patch review.

## References
- https://git.kernel.org/stable/c/06937db21ee311ed07eba47954447245041a982d
- https://git.kernel.org/stable/c/27856d533eca3804008695f61c1e4d5ff984196b
- https://git.kernel.org/stable/c/3b249988d774dacf13b203817e971934a42243c4
- https://git.kernel.org/stable/c/67a35e7da7ef9d2f000aa758552a128324c604a0
- https://git.kernel.org/stable/c/6bba24e9ebe6f1c0b356cd471e36bdc7fa434897
- https://git.kernel.org/stable/c/72158ea185b27afae163949b0e86164cb6b64e55
- https://git.kernel.org/stable/c/b6b22824b30e48ce1df3a2e80990f4b8505deb50
- https://git.kernel.org/stable/c/cfd62907f3cdbc3b6da8f49ba907c0390018fe5e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64056.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64056
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
