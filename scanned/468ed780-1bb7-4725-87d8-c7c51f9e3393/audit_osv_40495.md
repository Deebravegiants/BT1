# [H] ipv4: account for fraggap on the paged allocation path

## Summary
Severity: High
Advisory: CVE-2026-53366
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-16
Source: https://osv.dev/vulnerability/CVE-2026-53366
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.0.0 <6.1.178, >=6.2.0 <6.6.144, >=6.7.0 <6.12.95, >=6.13.0 <6.18.38, >=6.19.0 <7.1.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv4: account for fraggap on the paged allocation path

In __ip_append_data(), when the paged-allocation branch is taken,
alloclen and pagedlen are computed as

	alloclen = fragheaderlen + transhdrlen;
	pagedlen = datalen - transhdrlen;

datalen already includes fraggap, but the fraggap bytes carried over
from the previous skb are copied into the new skb's linear area at
offset transhdrlen by the subsequent skb_copy_and_csum_bits(). The
linear area is therefore undersized by fraggap bytes while pagedlen is
overstated by the same amount.

The non-paged branch sets alloclen to fraglen, which already accounts
for fraggap because datalen does. Bring the paged branch in line by
adding fraggap to alloclen and subtracting it from pagedlen.

After this adjustment, copy no longer collapses to -fraggap on the
paged path, so remove the stale comment describing that old arithmetic.

## References
- https://git.kernel.org/stable/c/5c6375bced6147ec2e460ee3b653f4860d5ecdc2
- https://git.kernel.org/stable/c/77798d7be6ef71e72fb6fc8a2901bf74ebc9706f
- https://git.kernel.org/stable/c/a9c24eda24bd15f432e37824e6fc440977cb241c
- https://git.kernel.org/stable/c/c04d9ece23deb9e26c19f9ca215e98b3295aa1bb
- https://git.kernel.org/stable/c/ce494707a9c07f27c219ca67f3e138061f53d9b3
- https://git.kernel.org/stable/c/eca856950f7cb1a221e02b99d758409f2c5cec42
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53366.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53366
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
