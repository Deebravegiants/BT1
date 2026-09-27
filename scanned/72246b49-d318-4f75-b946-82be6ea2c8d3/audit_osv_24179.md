# [M] media: mediatek: vcodec: Can't set dst buffer to done when lat decode error

## Summary
Severity: Medium
Advisory: CVE-2022-50383
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-18
Source: https://osv.dev/vulnerability/CVE-2022-50383
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.0.16, >=6.1.0 <6.1.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mediatek: vcodec: Can't set dst buffer to done when lat decode error

Core thread will call v4l2_m2m_buf_done to set dst buffer done for
lat architecture. If lat call v4l2_m2m_buf_done_and_job_finish to
free dst buffer when lat decode error, core thread will access kernel
NULL pointer dereference, then crash.

## References
- https://git.kernel.org/stable/c/3568ecd3f3a6d133ab7feffbba34955c8c79bbc4
- https://git.kernel.org/stable/c/66d26ed30056e7d2da3e9c14125ffe6049a4f907
- https://git.kernel.org/stable/c/eeb090420f3477eb5011586709409fc655c2b16c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/50xxx/CVE-2022-50383.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-50383
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
