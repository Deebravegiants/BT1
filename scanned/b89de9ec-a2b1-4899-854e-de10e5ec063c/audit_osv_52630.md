# [M] CVE-2021-47660

## Summary
Severity: Medium
Advisory: CVE-2021-47660
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2021-47660
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

fs/ntfs3: Fix some memory leaks in an error handling path of 'log_replay()'

All error handling paths lead to 'out' where many resources are freed.

Do it as well here instead of a direct return, otherwise 'log', 'ra' and
'log->one_page_buf' (at least) will leak.

## References
- https://git.kernel.org/stable/c/e589f9b7078e1c0191613cd736f598e81d2390de
- https://git.kernel.org/stable/c/2c97519ed6b4239594c58ddacf3d0d576cf070cc
- https://git.kernel.org/stable/c/bc4a1d384a04c6dba9312e1421a9f9f7c03339a4
- https://git.kernel.org/stable/c/d8be98ab88250dc12a98efdb703792a537b0eac3
