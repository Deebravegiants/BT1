# [H] crypto: caam - use print_hex_dump_devel to guard key hex dumps

## Summary
Severity: High
Advisory: CVE-2026-64315
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-25
Source: https://osv.dev/vulnerability/CVE-2026-64315
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.20.0 <5.10.261, >=5.11.0 <5.15.212, >=5.16.0 <6.1.178, >=6.2.0 <6.6.145, >=6.7.0 <6.12.96, >=6.13.0 <6.18.39, >=6.19.0 <7.1.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: caam - use print_hex_dump_devel to guard key hex dumps

Use print_hex_dump_devel() for dumping sensitive key material in
*_setkey() to avoid leaking secrets at runtime when CONFIG_DYNAMIC_DEBUG
is enabled.

## References
- https://git.kernel.org/stable/c/1ec775f6a124cce6278ae58b7d1c78a3bc6eef23
- https://git.kernel.org/stable/c/59057f5d4e9a195c6dd61695ad3bc4481ddf4f14
- https://git.kernel.org/stable/c/6407dc85d0a4306681cf6c9be7f05e05dcb67a37
- https://git.kernel.org/stable/c/8005dc808bcce7d6cc2ae015a3cde1683bee602d
- https://git.kernel.org/stable/c/8904b425cfcafe6a820c94b9bdf4b10f7d70f9d7
- https://git.kernel.org/stable/c/bcf3cf74dfb6981e18b22cbf561f859a0f7faa26
- https://git.kernel.org/stable/c/c8cfe11e48b2a4646fa662fcaa92e14810a28d46
- https://git.kernel.org/stable/c/d0b8cafd529b4ec759190c6081f7a76efb563a8f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/64xxx/CVE-2026-64315.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-64315
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
