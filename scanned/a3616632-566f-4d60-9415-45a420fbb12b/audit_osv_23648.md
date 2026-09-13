# [H] uaccess: fix integer overflow on access_ok()

## Summary
Severity: High
Advisory: CVE-2022-49289
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49289
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.2.0 <5.15.32, >=5.16.0 <5.16.18, >=5.17.0 <5.17.1

## Details
In the Linux kernel, the following vulnerability has been resolved:

uaccess: fix integer overflow on access_ok()

Three architectures check the end of a user access against the
address limit without taking a possible overflow into account.
Passing a negative length or another overflow in here returns
success when it should not.

Use the most common correct implementation here, which optimizes
for a constant 'size' argument, and turns the common case into a
single comparison.

## References
- https://git.kernel.org/stable/c/222ca305c9fd39e5ed8104da25c09b2b79a516a8
- https://git.kernel.org/stable/c/99801e2f457824955da4aadaa035913a6dede03a
- https://git.kernel.org/stable/c/a1ad747fc1a0e06d1bf26b996ee8a56b5c8d02d8
- https://git.kernel.org/stable/c/e65d28d4e9bf90a35ba79c06661a572a38391dec
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49289.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49289
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
