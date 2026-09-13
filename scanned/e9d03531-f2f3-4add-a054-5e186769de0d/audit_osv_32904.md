# [H] s390/pkey: Prevent overflow in size calculation for memdup_user()

## Summary
Severity: High
Advisory: CVE-2025-38257
Ecosystem: Linux
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:H)
Published: 2025-07-09
Source: https://osv.dev/vulnerability/CVE-2025-38257
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.4.0 <5.15.187, >=5.16.0 <6.1.143, >=6.2.0 <6.6.96, >=6.7.0 <6.12.36, >=6.13.0 <6.15.5

## Details
In the Linux kernel, the following vulnerability has been resolved:

s390/pkey: Prevent overflow in size calculation for memdup_user()

Number of apqn target list entries contained in 'nr_apqns' variable is
determined by userspace via an ioctl call so the result of the product in
calculation of size passed to memdup_user() may overflow.

In this case the actual size of the allocated area and the value
describing it won't be in sync leading to various types of unpredictable
behaviour later.

Use a proper memdup_array_user() helper which returns an error if an
overflow is detected. Note that it is different from when nr_apqns is
initially zero - that case is considered valid and should be handled in
subsequent pkey_handler implementations.

Found by Linux Verification Center (linuxtesting.org).

## References
- https://git.kernel.org/stable/c/73483ca7e07a5e39bdf612eec9d3d293e8bef649
- https://git.kernel.org/stable/c/7360ee47599af91a1d5f4e74d635d9408a54e489
- https://git.kernel.org/stable/c/88f3869649edbc4a13f6c2877091f81cd5a50f05
- https://git.kernel.org/stable/c/ad1bdd24a02d5a8d119af8e4cd50933780a6d29f
- https://git.kernel.org/stable/c/f855b119e62b004a5044ed565f2a2b368c4d3f16
- https://git.kernel.org/stable/c/faa1ab4a23c42e34dc000ef4977b751d94d5148c
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38257.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38257
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
