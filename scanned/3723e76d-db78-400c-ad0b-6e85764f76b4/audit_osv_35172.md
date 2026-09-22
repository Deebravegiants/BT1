# [H] tpm2-sessions: Fix out of range indexing in name_size

## Summary
Severity: High
Advisory: CVE-2025-68792
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-01-13
Source: https://osv.dev/vulnerability/CVE-2025-68792
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.66, >=6.13.0 <6.18.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

tpm2-sessions: Fix out of range indexing in name_size

'name_size' does not have any range checks, and it just directly indexes
with TPM_ALG_ID, which could lead into memory corruption at worst.

Address the issue by only processing known values and returning -EINVAL for
unrecognized values.

Make also 'tpm_buf_append_name' and 'tpm_buf_fill_hmac_session' fallible so
that errors are detected before causing any spurious TPM traffic.

End also the authorization session on failure in both of the functions, as
the session state would be then by definition corrupted.

## References
- https://git.kernel.org/stable/c/04a3aa6e8c5f878cc51a8a1c90b6d3c54079bc43
- https://git.kernel.org/stable/c/47e676ce4d68f461dfcab906f6aeb254f7276deb
- https://git.kernel.org/stable/c/6e9722e9a7bfe1bbad649937c811076acf86e1fd
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/68xxx/CVE-2025-68792.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-68792
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
