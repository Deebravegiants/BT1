# [H] media: vivid: fix buffer overwrite when using > 32 buffers

## Summary
Severity: High
Advisory: CVE-2024-50288
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-11-19
Source: https://osv.dev/vulnerability/CVE-2024-50288
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.11.8

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: vivid: fix buffer overwrite when using > 32 buffers

The maximum number of buffers that can be requested was increased to
64 for the video capture queue. But video capture used a must_blank
array that was still sized for 32 (VIDEO_MAX_FRAME). This caused an
out-of-bounds write when using buffer indices >= 32.

Create a new define MAX_VID_CAP_BUFFERS that is used to access the
must_blank array and set max_num_buffers for the video capture queue.

This solves a crash reported by:

	https://bugzilla.kernel.org/show_bug.cgi?id=219258

## References
- https://git.kernel.org/stable/c/96d8569563916fe2f8fe17317e20e43f54f9ba4b
- https://git.kernel.org/stable/c/e6bacd8f2178b22859fe6d9f755f19dfcd9d3862
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/50xxx/CVE-2024-50288.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-50288
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
