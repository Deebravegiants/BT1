# [H] ASoC: SOF: Add some bounds checking to firmware data

## Summary
Severity: High
Advisory: CVE-2024-26927
Ecosystem: Linux
CVSS: 8.4 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-04-28
Source: https://osv.dev/vulnerability/CVE-2024-26927
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.19.0 <6.1.83, >=6.2.0 <6.6.23, >=6.7.0 <6.7.11, >=6.8.0 <6.8.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

ASoC: SOF: Add some bounds checking to firmware data

Smatch complains about "head->full_size - head->header_size" can
underflow.  To some extent, we're always going to have to trust the
firmware a bit.  However, it's easy enough to add a check for negatives,
and let's add a upper bounds check as well.

## References
- https://git.kernel.org/stable/c/044e220667157fb9d59320341badec59cf45ba48
- https://git.kernel.org/stable/c/98f681b0f84cfc3a1d83287b77697679e0398306
- https://git.kernel.org/stable/c/9eeb8e1231f6450c574c1db979122e171a1813ab
- https://git.kernel.org/stable/c/ced7df8b3c5c4751244cad79011e86cf1f809153
- https://git.kernel.org/stable/c/d133d67e7e724102d1e53009c4f88afaaf3e167c
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26927.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-26927
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
