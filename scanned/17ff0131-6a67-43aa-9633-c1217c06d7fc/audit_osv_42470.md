# [H] media: v4l2-ctrls: validate HEVC active reference counts

## Summary
Severity: High
Advisory: CVE-2026-68206
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-08-10
Source: https://osv.dev/vulnerability/CVE-2026-68206
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <6.1.183, >=6.2.0 <6.6.148, >=6.7.0 <6.12.101, >=6.13.0 <6.18.42, >=6.19.0 <7.1.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: v4l2-ctrls: validate HEVC active reference counts

HEVC slice parameters are shared stateless V4L2 controls, but the common
validation path does not verify the active L0/L1 reference counts before
driver-specific code consumes them.

The original report came from Cedrus, but the active count bounds are
not Cedrus-specific. Validate them in the common HEVC slice control path
so stateless HEVC drivers get the same basic guarantees as soon as the
control is queued.

Do not reject ref_idx_l0/ref_idx_l1 entries here. Existing userspace may
use out-of-range sentinel values such as 0xff for missing references, and
some hardware can use that information for concealment. Keep this common
check limited to the active reference counts.

## References
- https://git.kernel.org/stable/c/3068ab802fc98b121dcb451e1f7f4d338ffc7a19
- https://git.kernel.org/stable/c/3299c3905f3fb439ebd892658b87bc76c93ae116
- https://git.kernel.org/stable/c/9a998cc1c348769262d433acb7d238c5fac4b2e0
- https://git.kernel.org/stable/c/afbe4bc252d90a6f8fad869b06d5430f615f22f9
- https://git.kernel.org/stable/c/b01df98a6669d2b67d8aed816021b327fd905998
- https://git.kernel.org/stable/c/dbaf0e0023e2f9332c5164822def7f80b7d2c5ef
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/68xxx/CVE-2026-68206.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-68206
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
