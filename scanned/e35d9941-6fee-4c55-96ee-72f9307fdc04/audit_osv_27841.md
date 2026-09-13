# [H] KVM: arm64: vgic-its: Avoid potential UAF in LPI translation cache

## Summary
Severity: High
Advisory: CVE-2024-26598
Ecosystem: Linux
CVSS: 8.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-02-23
Source: https://osv.dev/vulnerability/CVE-2024-26598
Type: osv

## Affected
- Linux: `Kernel` — affected >=3.11.0 <5.4.269, >=5.5.0 <5.10.209, >=5.11.0 <5.15.148, >=5.16.0 <6.1.75, >=6.2.0 <6.6.14, >=6.7.0 <6.7.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

KVM: arm64: vgic-its: Avoid potential UAF in LPI translation cache

There is a potential UAF scenario in the case of an LPI translation
cache hit racing with an operation that invalidates the cache, such
as a DISCARD ITS command. The root of the problem is that
vgic_its_check_cache() does not elevate the refcount on the vgic_irq
before dropping the lock that serializes refcount changes.

Have vgic_its_check_cache() raise the refcount on the returned vgic_irq
and add the corresponding decrement after queueing the interrupt.

## References
- https://git.kernel.org/stable/c/12c2759ab1343c124ed46ba48f27bd1ef5d2dff4
- https://git.kernel.org/stable/c/65b201bf3e9af1b0254243a5881390eda56f72d1
- https://git.kernel.org/stable/c/ad362fe07fecf0aba839ff2cc59a3617bd42c33f
- https://git.kernel.org/stable/c/ba7be666740847d967822bed15500656b26bc703
- https://git.kernel.org/stable/c/d04acadb6490aa3314f9c9e087691e55de153b88
- https://git.kernel.org/stable/c/dba788e25f05209adf2b0175eb1691dc89fb1ba6
- https://git.kernel.org/stable/c/dd3956a1b3dd11f46488c928cb890d6937d1ca80
- https://lists.debian.org/debian-lts-announce/2024/06/msg00016.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26598.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26598
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
