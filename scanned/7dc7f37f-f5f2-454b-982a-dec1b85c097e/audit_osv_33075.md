# [H] gfs2: Validate i_depth for exhash directories

## Summary
Severity: High
Advisory: CVE-2025-38710
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-04
Source: https://osv.dev/vulnerability/CVE-2025-38710
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.26 <5.10.258, >=5.11.0 <5.15.209, >=5.16.0 <6.1.175, >=6.2.0 <6.6.134, >=6.7.0 <6.12.43, >=6.13.0 <6.15.11, >=6.16.0 <6.16.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

gfs2: Validate i_depth for exhash directories

A fuzzer test introduced corruption that ends up with a depth of 0 in
dir_e_read(), causing an undefined shift by 32 at:

  index = hash >> (32 - dip->i_depth);

As calculated in an open-coded way in dir_make_exhash(), the minimum
depth for an exhash directory is ilog2(sdp->sd_hash_ptrs) and 0 is
invalid as sdp->sd_hash_ptrs is fixed as sdp->bsize / 16 at mount time.

So we can avoid the undefined behaviour by checking for depth values
lower than the minimum in gfs2_dinode_in(). Values greater than the
maximum are already being checked for there.

Also switch the calculation in dir_make_exhash() to use ilog2() to
clarify how the depth is calculated.

Tested with the syzkaller repro.c and xfstests '-g quick'.

## References
- https://git.kernel.org/stable/c/076e992752e4b24178918f748d75597c80a408d2
- https://git.kernel.org/stable/c/112bb60cd0e254a369e95aa9941a694ffeca089f
- https://git.kernel.org/stable/c/366183911b153e9b8cf758e1414e1154d7569337
- https://git.kernel.org/stable/c/53a0249d68a210c16e961b83adfa82f94ee0a53d
- https://git.kernel.org/stable/c/557c024ca7250bb65ae60f16c02074106c2f197b
- https://git.kernel.org/stable/c/9680c58675b82348ab84d387e4fa727f7587e1a0
- https://git.kernel.org/stable/c/b5f46951e62377b6e406fadc18bc3c5bdf1632a7
- https://git.kernel.org/stable/c/cddea0c721106ea480371412d8de21705eb27376
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38710.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38710
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
