# [H] drm/v3d: Prevent out of bounds access in performance query extensions

## Summary
Severity: High
Advisory: CVE-2024-42264
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-08-17
Source: https://osv.dev/vulnerability/CVE-2024-42264
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.10.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/v3d: Prevent out of bounds access in performance query extensions

Check that the number of perfmons userspace is passing in the copy and
reset extensions is not greater than the internal kernel storage where
the ids will be copied into.

(cherry picked from commit f32b5128d2c440368b5bf3a7a356823e235caabb)

## References
- https://git.kernel.org/stable/c/6ce9efd12ae81cf46bf44eb0348594558dfbb9d2
- https://git.kernel.org/stable/c/73ad583bd4938bf37d2709fc36901eb6f22f2722
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42264.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42264
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
