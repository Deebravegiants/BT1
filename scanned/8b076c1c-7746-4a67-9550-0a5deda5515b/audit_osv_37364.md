# [H] netfilter: conntrack: add missing netlink policy validations

## Summary
Severity: High
Advisory: CVE-2026-31407
Ecosystem: Linux
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-04-06
Source: https://osv.dev/vulnerability/CVE-2026-31407
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.27 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.83, >=6.13.0 <6.18.24, >=6.19.0 <6.19.10

## Details
In the Linux kernel, the following vulnerability has been resolved:

netfilter: conntrack: add missing netlink policy validations

Hyunwoo Kim reports out-of-bounds access in sctp and ctnetlink.

These attributes are used by the kernel without any validation.
Extend the netlink policies accordingly.

Quoting the reporter:
  nlattr_to_sctp() assigns the user-supplied CTA_PROTOINFO_SCTP_STATE
  value directly to ct->proto.sctp.state without checking that it is
  within the valid range. [..]

  and: ... with exp->dir = 100, the access at
  ct->master->tuplehash[100] reads 5600 bytes past the start of a
  320-byte nf_conn object, causing a slab-out-of-bounds read confirmed by
  UBSAN.

## References
- https://git.kernel.org/stable/c/0fbae1e74493d5a160a70c51aeba035d8266ea7d
- https://git.kernel.org/stable/c/67c53c1978cef3c504237275e39c857e2f6af56e
- https://git.kernel.org/stable/c/78bba9f73942aa7dca47d817d8cec0fb9b443b70
- https://git.kernel.org/stable/c/9174d28f3f15d8c4962f5980c0be167633880443
- https://git.kernel.org/stable/c/be88a337bf07afb1ee173f1099294d1b7ab3fefe
- https://git.kernel.org/stable/c/c5e918390002edf0cff80a0e7ce1f86f16a9507c
- https://git.kernel.org/stable/c/e7b5766693477c52424cc6c79dd30a7a9c7db52c
- https://git.kernel.org/stable/c/f900e1d77ee0ef87bfb5ab3fe60f0b3d8ad5ba05
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31407.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31407
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
