# [H] drm/panfrost: Job should reference MMU not file_priv

## Summary
Severity: High
Advisory: CVE-2022-49359
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49359
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.17.15, >=5.18.0 <5.18.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/panfrost: Job should reference MMU not file_priv

For a while now it's been allowed for a MMU context to outlive it's
corresponding panfrost_priv, however the job structure still references
panfrost_priv to get hold of the MMU context. If panfrost_priv has been
freed this is a use-after-free which I've been able to trigger resulting
in a splat.

To fix this, drop the reference to panfrost_priv in the job structure
and add a direct reference to the MMU structure which is what's actually
needed.

## References
- https://git.kernel.org/stable/c/472dd7ea5e19a1aeabf1711ddc756777e05ee7c2
- https://git.kernel.org/stable/c/6e516faf04317db2c46cbec4e3b78b4653a5b109
- https://git.kernel.org/stable/c/8c8e8cc91a6ffc79865108279a74fd57d9070a17
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49359.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49359
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
