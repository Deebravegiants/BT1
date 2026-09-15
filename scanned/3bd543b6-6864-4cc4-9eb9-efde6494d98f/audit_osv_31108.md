# [H] xfrm: state: fix out-of-bounds read during lookup

## Summary
Severity: High
Advisory: CVE-2024-57982
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-27
Source: https://osv.dev/vulnerability/CVE-2024-57982
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.9.0 <6.6.120, >=6.7.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

xfrm: state: fix out-of-bounds read during lookup

lookup and resize can run in parallel.

The xfrm_state_hash_generation seqlock ensures a retry, but the hash
functions can observe a hmask value that is too large for the new hlist
array.

rehash does:
  rcu_assign_pointer(net->xfrm.state_bydst, ndst) [..]
  net->xfrm.state_hmask = nhashmask;

While state lookup does:
  h = xfrm_dst_hash(net, daddr, saddr, tmpl->reqid, encap_family);
  hlist_for_each_entry_rcu(x, net->xfrm.state_bydst + h, bydst) {

This is only safe in case the update to state_bydst is larger than
net->xfrm.xfrm_state_hmask (or if the lookup function gets
serialized via state spinlock again).

Fix this by prefetching state_hmask and the associated pointers.
The xfrm_state_hash_generation seqlock retry will ensure that the pointer
and the hmask will be consistent.

The existing helpers, like xfrm_dst_hash(), are now unsafe for RCU side,
add lockdep assertions to document that they are only safe for insert
side.

xfrm_state_lookup_byaddr() uses the spinlock rather than RCU.
AFAICS this is an oversight from back when state lookup was converted to
RCU, this lock should be replaced with RCU in a future patch.

## References
- https://git.kernel.org/stable/c/a16871c7832ea6435abb6e0b58289ae7dcb7e4fc
- https://git.kernel.org/stable/c/b86dc510308d7a8955f3f47a4fea4bef887653e4
- https://git.kernel.org/stable/c/dd4c2a174994238d55ab54da2545543d36f4e0d0
- https://git.kernel.org/stable/c/e952837f3ddb0ff726d5b582aa1aad9aa38d024d
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/57xxx/CVE-2024-57982.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-57982
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
