# [C] ipvs: fix more places with wrong ipv6 transport offsets

## Summary
Severity: Critical
Advisory: CVE-2026-68477
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-15
Source: https://osv.dev/vulnerability/CVE-2026-68477
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.28 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.97, >=6.13.0 <6.18.40, >=6.19.0 <7.1.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: fix more places with wrong ipv6 transport offsets

Sashiko reports for more incorrect IPv6 transport offsets.

The app code for TCP was assuming IPv4 network header
even after the ipvsh argument was provided. This can
cause problems with apps over IPv6. As for the only
official app in the kernel tree (FTP) this problem is
harmless because we use Netfilter to mangle the FTP
ports and we do not adjust the TCP seq numbers.

Also, provide correct offset of the ICMPV6 header in
ip_vs_out_icmp_v6() for correct checksum checks when
the IPv6 packet has extension headers.

## References
- https://git.kernel.org/stable/c/3a9dc9b55b53d94613a587604b77d3b20024090c
- https://git.kernel.org/stable/c/613ce63711b8d431bba90781f133c39a21684f87
- https://git.kernel.org/stable/c/7350eb7ead172ae8024897d4b0f2e15c5318279c
- https://git.kernel.org/stable/c/905d7a363ade96a19f214815361e11981142c547
- https://git.kernel.org/stable/c/95d4511d81b2b37e5d2bdde5d912e48243eae517
- https://git.kernel.org/stable/c/a3f0d5b605cd5da5c95279969fb8cea4e55cee5b
- https://git.kernel.org/stable/c/b3fe4cbd583895987935a9bdad01c8f9d3a02310
- https://git.kernel.org/stable/c/d4ec18f48ce78a3bf7c999ac908691007375fe99
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68477.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68477
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
