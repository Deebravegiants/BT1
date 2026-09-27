# [H] drm/amd/display: Check correct bounds for stream encoder instances for DCN303

## Summary
Severity: High
Advisory: CVE-2022-50079
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-18
Source: https://osv.dev/vulnerability/CVE-2022-50079
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.14.0 <5.15.63, >=5.16.0 <5.19.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Check correct bounds for stream encoder instances for DCN303

[Why & How]
eng_id for DCN303 cannot be more than 1, since we have only two
instances of stream encoders.

Check the correct boundary condition for engine ID for DCN303 prevent
the potential out of bounds access.

## References
- https://git.kernel.org/stable/c/4c31dca1799612eb3b6413e3e574f90c3fb8f865
- https://git.kernel.org/stable/c/82a27c1855445d48aacc67b0c0640f3dadebe52f
- https://git.kernel.org/stable/c/89b008222c2bf21e50219725caed31590edfd9d1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50079.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50079
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
