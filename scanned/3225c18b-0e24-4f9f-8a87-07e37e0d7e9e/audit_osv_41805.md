# [C] xfrm: esp: restore combined single-frag length gate

## Summary
Severity: Critical
Advisory: CVE-2026-63912
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-19
Source: https://osv.dev/vulnerability/CVE-2026-63912
Type: osv

## Affected
- Linux: `Kernel` — affected >=0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.176, >=5.18.0 <6.6.143, >=6.2.0 <6.12.93, >=6.7.0 <6.18.35, >=6.13.0 <7.0.12

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: esp: restore combined single-frag length gate

The ESP out-of-place fast path appends the trailer in esp_output_head()
before esp_output_tail() allocates the destination page frag. The
head-side gate currently checks skb->data_len and tailen separately, but
the tail code allocates a single destination frag from the combined
post-trailer skb->data_len.

Reject the page-frag fast path when the combined aligned length exceeds a
page. Otherwise skb_page_frag_refill() may fall back to a single page while
the destination sg still spans the combined skb->data_len.

Restore this combined-length page gate for both IPv4 and IPv6.

## References
- https://git.kernel.org/stable/c/322e48187e0245ab2fff6fec2220b0cae677dbec
- https://git.kernel.org/stable/c/36519e3d941fc99d3b52c134dbaf311f987a4708
- https://git.kernel.org/stable/c/566295735530ee513326049b0540f32ec050bf2e
- https://git.kernel.org/stable/c/5d7ab86e2b6bc23054616bf6ac562013bf60af8c
- https://git.kernel.org/stable/c/65f3b3fc2347b89fe21db1e92c7681368415f095
- https://git.kernel.org/stable/c/b84091ceddc9f133229dceab3ccc930bf27f9cba
- https://git.kernel.org/stable/c/c093468aea8277f77272a4f199b2e15e19cabb59
- https://git.kernel.org/stable/c/dfa0d7b0ff1eb6b2c416b8fdb9b4f2cefba57a40
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/63xxx/CVE-2026-63912.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-63912
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
