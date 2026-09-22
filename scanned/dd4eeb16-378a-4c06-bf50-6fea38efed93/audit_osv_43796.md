# [H] ipvs: revalidate ihl to prevent out-of-bounds access

## Summary
Severity: High
Advisory: CVE-2026-74747
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-26
Source: https://osv.dev/vulnerability/CVE-2026-74747
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <7.1.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipvs: revalidate ihl to prevent out-of-bounds access

While the outer IP header is already pulled into the skb head,
we must be careful and revalidate the embedded headers after
reading them from the skb frags to prevent out-of-bounds
access.

One such place reported by Sashiko is ip_vs_nat_icmp() where
local process can change the ihl field and after
skb_ensure_writable() we can see larger value which is a
problem for the ip_send_check(cih) calls.

Add check to drop the packet if the ihl field is changed.

## References
- https://git.kernel.org/stable/c/5365f012451fce2453f13a568dcb72ea534c1e4d
- https://git.kernel.org/stable/c/d93660df4dd1d116f608ada4a29a80a5d6f0a6ed
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74747.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74747
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
