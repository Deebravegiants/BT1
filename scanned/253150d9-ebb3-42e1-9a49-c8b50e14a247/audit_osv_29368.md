# [H] drm/amdgpu: fix double free err_addr pointer warnings

## Summary
Severity: High
Advisory: CVE-2024-42123
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-30
Source: https://osv.dev/vulnerability/CVE-2024-42123
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.2.0 <6.9.9

## Details
In the Linux kernel, the following vulnerability has been resolved:

drm/amdgpu: fix double free err_addr pointer warnings

In amdgpu_umc_bad_page_polling_timeout, the amdgpu_umc_handle_bad_pages
will be run many times so that double free err_addr in some special case.
So set the err_addr to NULL to avoid the warnings.

## References
- https://git.kernel.org/stable/c/506c245f3f1cd989cb89811a7f06e04ff8813a0d
- https://git.kernel.org/stable/c/8e24beb3c2b08a4763f920399a9cc577ed440a1a
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/42xxx/CVE-2024-42123.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-42123
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
