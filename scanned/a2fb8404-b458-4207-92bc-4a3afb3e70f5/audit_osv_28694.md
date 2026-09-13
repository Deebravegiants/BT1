# [H] media: mediatek: vcodec: adding lock to protect encoder context list

## Summary
Severity: High
Advisory: CVE-2024-35919
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-05-19
Source: https://osv.dev/vulnerability/CVE-2024-35919
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.6.0 <6.6.27, >=6.7.0 <6.8.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

media: mediatek: vcodec: adding lock to protect encoder context list

Add a lock for the ctx_list, to avoid accessing a NULL pointer
within the 'vpu_enc_ipi_handler' function when the ctx_list has
been deleted due to an unexpected behavior on the SCP IP block.

## References
- https://git.kernel.org/stable/c/41671f0c0182b2bae74ca7e3b0f155559e3e2fc5
- https://git.kernel.org/stable/c/51c84a8aac6e3b59af2b0e92ba63cabe2e641a2d
- https://git.kernel.org/stable/c/afaaf3a0f647a24a7bf6a2145d8ade37baaf75ad
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/35xxx/CVE-2024-35919.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-35919
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
