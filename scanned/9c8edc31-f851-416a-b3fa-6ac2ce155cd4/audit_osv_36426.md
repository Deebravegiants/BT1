# [H] netfilter: nf_conntrack_sip: fix Content-Length u32 truncation in sip_help_tcp()

## Summary
Severity: High
Advisory: CVE-2026-23457
Ecosystem: Linux
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:H)
Published: 2026-04-03
Source: https://osv.dev/vulnerability/CVE-2026-23457
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.34 <5.10.253, >=5.11.0 <5.15.203, >=5.16.0 <6.1.167, >=6.2.0 <6.6.130, >=6.7.0 <6.12.78, >=6.13.0 <6.18.20, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: nf_conntrack_sip: fix Content-Length u32 truncation in sip_help_tcp()

sip_help_tcp() parses the SIP Content-Length header with
simple_strtoul(), which returns unsigned long, but stores the result in
unsigned int clen.  On 64-bit systems, values exceeding UINT_MAX are
silently truncated before computing the SIP message boundary.

For example, Content-Length 4294967328 (2^32 + 32) is truncated to 32,
causing the parser to miscalculate where the current message ends.  The
loop then treats trailing data in the TCP segment as a second SIP
message and processes it through the SDP parser.

Fix this by changing clen to unsigned long to match the return type of
simple_strtoul(), and reject Content-Length values that exceed the
remaining TCP payload length.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-019113.html
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/528b4509c9dfc272e2e92d811915e5211650d383
- https://git.kernel.org/stable/c/75fcaee5170e7dbbee778927134ef2e9568b4659
- https://git.kernel.org/stable/c/865dba58958c3a86786f89a501971ab0e3ec6ba9
- https://git.kernel.org/stable/c/b75209debb9adab287b3caa982f77788c1e15027
- https://git.kernel.org/stable/c/cd1b7403ec835f8a0b3f1f7e68ac26af2cb1e42f
- https://git.kernel.org/stable/c/d4f17256544cc37f6534a14a27a9dec3540c2015
- https://git.kernel.org/stable/c/ed81b6a7012485acdb9c6c80735a0b7d8e5e1873
- https://git.kernel.org/stable/c/fbce58e719a17aa215c724473fd5baaa4a8dc57c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23457.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-23457
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
