# [H] io_uring/futex: ensure io_futex_wait() cleans up properly on failure

## Summary
Severity: High
Advisory: CVE-2025-39698
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-09-05
Source: https://osv.dev/vulnerability/CVE-2025-39698
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.7.0 <6.12.44, >=6.13.0 <6.16.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

io_uring/futex: ensure io_futex_wait() cleans up properly on failure

The io_futex_data is allocated upfront and assigned to the io_kiocb
async_data field, but the request isn't marked with REQ_F_ASYNC_DATA
at that point. Those two should always go together, as the flag tells
io_uring whether the field is valid or not.

Additionally, on failure cleanup, the futex handler frees the data but
does not clear ->async_data. Clear the data and the flag in the error
path as well.

Thanks to Trend Micro Zero Day Initiative and particularly ReDress for
reporting this.

## References
- https://git.kernel.org/stable/c/508c1314b342b78591f51c4b5dadee31a88335df
- https://git.kernel.org/stable/c/d34c04152df517c59979b4bf2a47f491e06d3256
- https://git.kernel.org/stable/c/d9f93172820a53ab42c4b0e5e65291f4f9d00ad2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/39xxx/CVE-2025-39698.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-39698
- https://www.zerodayinitiative.com/advisories/ZDI-25-915/
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
