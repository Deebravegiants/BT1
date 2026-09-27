# [H] smb: client: fix OOB read in smb2_ioctl_query_info QUERY_INFO path

## Summary
Severity: High
Advisory: CVE-2026-31708
Ecosystem: Linux
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:H)
Published: 2026-05-01
Source: https://osv.dev/vulnerability/CVE-2026-31708
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.1.0 <5.10.259, >=5.11.0 <5.15.210, >=5.16.0 <6.1.175, >=6.2.0 <6.6.136, >=6.7.0 <6.12.84, >=6.13.0 <6.18.25, >=6.19.0 <7.0.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

smb: client: fix OOB read in smb2_ioctl_query_info QUERY_INFO path

smb2_ioctl_query_info() has two response-copy branches: PASSTHRU_FSCTL
and the default QUERY_INFO path.  The QUERY_INFO branch clamps
qi.input_buffer_length to the server-reported OutputBufferLength and then
copies qi.input_buffer_length bytes from qi_rsp->Buffer to userspace, but
it never verifies that the flexible-array payload actually fits within
rsp_iov[1].iov_len.

A malicious server can return OutputBufferLength larger than the actual
QUERY_INFO response, causing copy_to_user() to walk past the response
buffer and expose adjacent kernel heap to userspace.

Guard the QUERY_INFO copy with a bounds check on the actual Buffer
payload.  Use struct_size(qi_rsp, Buffer, qi.input_buffer_length)
rather than an open-coded addition so the guard cannot overflow on
32-bit builds.

## References
- https://git.kernel.org/stable/c/078fae8f50adebb903ccf2252b44391324571e78
- https://git.kernel.org/stable/c/1dd757379997b71a328a4b591ffaf481acd0ead1
- https://git.kernel.org/stable/c/85fd46ee26a11841c670449508025965f61ce131
- https://git.kernel.org/stable/c/9e203dbb5402897c43130fb171a2617008a91f45
- https://git.kernel.org/stable/c/a34d456934fe42e4da5d2cc07787bf418bee99c6
- https://git.kernel.org/stable/c/a58c5af19ff0d6f44f6e9fe31e33a2c92223f77e
- https://git.kernel.org/stable/c/ac2f14e4705d020f04e806efa0d49ab8dc2b145f
- https://git.kernel.org/stable/c/e66bdc0704977ecee667a81d38255b579c2353d0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/31xxx/CVE-2026-31708.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-31708
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
