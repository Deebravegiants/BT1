# [M] drm/amd/display: Prevent crash when disable stream

## Summary
Severity: Medium
Advisory: CVE-2024-35799
Ecosystem: Linux
CVSS: 6.2 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-05-17
Source: https://osv.dev/vulnerability/CVE-2024-35799
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <6.6.26, >=6.7.0 <6.7.12, >=6.8.0 <6.8.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Prevent crash when disable stream

[Why]
Disabling stream encoder invokes a function that no longer exists.

[How]
Check if the function declaration is NULL in disable stream encoder.

## References
- https://git.kernel.org/stable/c/2b17133a0a2e0e111803124dad09e803718d4a48
- https://git.kernel.org/stable/c/4356a2c3f296503c8b420ae8adece053960a9f06
- https://git.kernel.org/stable/c/59772327d439874095516673b4b30c48bd83ca38
- https://git.kernel.org/stable/c/72d72e8fddbcd6c98e1b02d32cf6f2b04e10bd1c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35799.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35799
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
