# [H] ipv6: fix Route Information option length validation

## Summary
Severity: High
Advisory: CVE-2026-74598
Ecosystem: Linux
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-22
Source: https://osv.dev/vulnerability/CVE-2026-74598
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.17 <5.10.265, >=5.11.0 <5.15.216, >=5.16.0 <6.1.183, >=6.2.0 <6.6.152, >=6.7.0 <6.12.104, >=6.13.0 <6.18.45, >=6.19.0 <7.1.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

ipv6: fix Route Information option length validation

rt6_route_rcv() validates the Route Information option (RFC 4191) length
against the prefix length, but both checks are off by one.

rinfo->length is the ND option length in units of 8 octets and it
*includes* the 8-byte option header, so an option carrying N bytes of
prefix has length == 1 + N/8.  RFC 4191 section 2.3 requires length 3
when Prefix Length is greater than 64, and 2 or 3 when it is greater
than 0.  The code accepts length >= 2 and length >= 1 respectively.

ipv6_addr_prefix() then copies prefix_len/8 bytes out of rinfo->prefix,
so a Router Advertisement with (prefix_len=128, length=2) or
(prefix_len=64, length=1) makes the kernel read up to 8 bytes past the
end of the option.  Those bytes end up in the prefix of the route that
gets installed, so they are visible to userspace:

  # RA with a Route Information option (prefix_len=128, length=2)
  # followed by a source link-layer address option, 01 01 de ad be ef ca fe
  $ ip -6 route show
  2001:db8:dead:beef:101:dead:beef:cafe via fe80::1234 dev veth0 proto ra
                     ^^^^^^^^^^^^^^^^^^ the next option, read out of bounds

When the Route Information option is the last one in the packet, those
eight bytes come from the skb tail room instead.

Reject the option lengths RFC 4191 does not allow.

## References
- https://git.kernel.org/stable/c/0b9e02f3bd31c888f2ccdc0ca08e546d6abe9c4d
- https://git.kernel.org/stable/c/2f6f94eda12430fb41b24b44a71e2ea4e93561d7
- https://git.kernel.org/stable/c/3b2231e358d26e3aec5d8040b1fb777af03c5f05
- https://git.kernel.org/stable/c/7309529f257ae18e72112ef9f614edfd6df229bb
- https://git.kernel.org/stable/c/7eac87396c44a312be457ef41d4c5687883be9a2
- https://git.kernel.org/stable/c/d1ad8fb2ac6a1afb71dc22d9ae8efb4dda96c824
- https://git.kernel.org/stable/c/da64ed1f346ba84df574d6469fa2e422b2511719
- https://git.kernel.org/stable/c/ff3cb05289b8a4ef95fa7ea14c7d34818359edbb
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/74xxx/CVE-2026-74598.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-74598
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
