# [H] crypto: tegra - do not transfer req when tegra init fails

## Summary
Severity: High
Advisory: CVE-2024-58075
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-03-06
Source: https://osv.dev/vulnerability/CVE-2024-58075
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.10.0 <6.12.13, >=6.13.0 <6.13.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: tegra - do not transfer req when tegra init fails

The tegra_cmac_init or tegra_sha_init function may return an error when
memory is exhausted. It should not transfer the request when they return
an error.

## References
- https://git.kernel.org/stable/c/15589bda46830695a3261518bb7627afac61f519
- https://git.kernel.org/stable/c/1dbc270f9df7f0ae1e591323431869059cee1b7d
- https://git.kernel.org/stable/c/5eaa7c916e1ec4b122a1c3a8a20e692d9d9e174e
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/58xxx/CVE-2024-58075.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-58075
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
