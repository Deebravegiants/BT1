# [C] smb: client: reject overlapping data areas in SMB2 responses

## Summary
Severity: Critical
Advisory: CVE-2026-64257
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64257
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: reject overlapping data areas in SMB2 responses

Commit 53b7c271f06b ("smb: client: restrict implied bcc[0] exemption to
responses without data area") restricted the implied bcc[0] length
exception to responses without a data area. However, the overlap
handling in __smb2_calc_size() clears data_length, which can make an
invalid response appear to have no data area and so qualify for the
exception.

Track data area overlap separately and reject such responses before
applying the length compatibility exceptions.

## References
- https://git.kernel.org/stable/c/36bfa52459e45c0d5b668de2f1c91f6dc5c67775
- https://git.kernel.org/stable/c/445ece263131780dee273d727a4d6f11934feec7
- https://git.kernel.org/stable/c/4a9d2657d3e05f6ed09c148cb127b4e58702275f
- https://git.kernel.org/stable/c/57cba95f0e97c6f6e45e6731da30aff091bd7460
- https://git.kernel.org/stable/c/8986c932905ea508d66da421eb2eb6e676ace1fe
- https://git.kernel.org/stable/c/fdafa1e68dc75045b7b617e6e7d2854950804d83
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64257.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64257
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
