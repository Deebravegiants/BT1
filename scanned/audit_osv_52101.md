# [M] CVE-2021-47071

## Summary
Severity: Medium
Advisory: CVE-2021-47071
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-03-01
Source: https://osv.dev/vulnerability/CVE-2021-47071
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

uio_hv_generic: Fix a memory leak in error handling paths

If 'vmbus_establish_gpadl()' fails, the (recv|send)_gpadl will not be
updated and 'hv_uio_cleanup()' in the error handling path will not be
able to free the corresponding buffer.

In such a case, we need to free the buffer explicitly.

## References
- https://git.kernel.org/stable/c/cdd91637d4ef33e2be19a8e16e72e7d00c996d76
- https://git.kernel.org/stable/c/d84b5e912212b05f6b5bde9f682046accfbe0354
- https://git.kernel.org/stable/c/3ee098f96b8b6c1a98f7f97915f8873164e6af9d
- https://git.kernel.org/stable/c/53486c467e356e06aa37047c984fccd64d78c827
