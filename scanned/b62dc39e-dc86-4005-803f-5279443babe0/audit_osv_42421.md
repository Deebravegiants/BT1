# [H] rtase: Workaround for TX hang caused by hardware packet parsing

## Summary
Severity: High
Advisory: CVE-2026-68120
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68120
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.12.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

rtase: Workaround for TX hang caused by hardware packet parsing

The hardware performs packet parsing before packet transmission.
Parsing incomplete IPv4, IPv6, TCP, or UDP headers may trigger a TX
hang because the hardware parser expects additional protocol header
data that is not present in the packet.

The hardware performs additional PTP parsing on UDP packets identified
by destination ports 319/320 at the expected UDP destination port
offset.

If such a packet has transport data smaller than RTASE_MIN_PAD_LEN,
the hardware parser expects additional packet data and may trigger a
TX hang.

To avoid these hardware issues, the driver applies the following
workarounds.

Drop malformed packets that may trigger this hardware issue before
transmission.

For IPv4 non-initial fragments, the hardware does not check the
fragment offset before parsing the expected transport header location.
As a result, these packets are still subject to transport header
parsing even though they do not contain a transport header. If the
transport data is shorter than the minimum transport header required
by the hardware parser, pad the transport data to the minimum
transport header length required by the hardware parser. Packets that
also match the hardware PTP parsing conditions continue to follow the
corresponding workaround.

For IPv6 fragmented packets, neither of the above hardware issues
occurs because the hardware only continues packet parsing when the
IPv6 Base Header Next Header field directly indicates UDP. Packets
carrying a Fragment Header do not continue through the subsequent
packet parsing stages.

For packets identified for hardware PTP parsing, pad the transport
data so it reaches RTASE_MIN_PAD_LEN before transmission.

## References
- https://git.kernel.org/stable/c/0f54f5048615e4e2802697855ea6374613548301
- https://git.kernel.org/stable/c/1c50efa1faf3a1a96e100b07ec7a2f3164d90bee
- https://git.kernel.org/stable/c/4a4f3aa6af205bee539b5670afa2cd4e4953750e
- https://git.kernel.org/stable/c/fe3a7320711eec6537e4890892f7ab9776d8618f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68120.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68120
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
