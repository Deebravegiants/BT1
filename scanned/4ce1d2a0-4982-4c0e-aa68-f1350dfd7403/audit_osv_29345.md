# [H] drm/amd/display: Skip pipe if the pipe idx not set properly

## Summary
Severity: High
Advisory: CVE-2024-42064
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-29
Source: https://osv.dev/vulnerability/CVE-2024-42064
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.9.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Skip pipe if the pipe idx not set properly

[why]
Driver crashes when pipe idx not set properly

[how]
Add code to skip the pipe that idx not set properly

## References
- https://git.kernel.org/stable/c/27df59c6071470efce7182ee92fbb16afba551e0
- https://git.kernel.org/stable/c/af114efe8d24b5711cfbedf7180f2ac1a296c24b
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42064.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42064
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
