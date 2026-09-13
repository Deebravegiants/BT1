# [H] drm/amd/display: Stop amdgpu_dm initialize when link nums greater than max_links

## Summary
Severity: High
Advisory: CVE-2024-46816
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46816
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.15.0 <5.10.237, >=5.11.0 <5.15.181, >=5.16.0 <6.1.135, >=6.2.0 <6.6.88, >=6.7.0 <6.10.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amd/display: Stop amdgpu_dm initialize when link nums greater than max_links

[Why]
Coverity report OVERRUN warning. There are
only max_links elements within dc->links. link
count could up to AMDGPU_DM_MAX_DISPLAY_INDEX 31.

[How]
Make sure link count less than max_links.

## References
- https://git.kernel.org/stable/c/13080d052c995aee14695a5b740c245121eb2bcc
- https://git.kernel.org/stable/c/36c39a8dcce210649f2f45f252abaa09fcc1ae87
- https://git.kernel.org/stable/c/c84632096722fd31251f0957fafc9e90d9a247fd
- https://git.kernel.org/stable/c/cf8b16857db702ceb8d52f9219a4613363e2b1cf
- https://git.kernel.org/stable/c/e2411b6abf6e5d6c33d0450846673cdf536f0ba4
- https://git.kernel.org/stable/c/e3cd0d8362de47f613bfdf315b3f3a9ab71e66bf
- https://lists.debian.org/debian-lts-announce/2025/05/msg00030.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00045.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46816.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46816
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
