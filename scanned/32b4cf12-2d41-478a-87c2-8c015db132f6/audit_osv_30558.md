# [M] clk: clk-apple-nco: Add NULL check in applnco_probe

## Summary
Severity: Medium
Advisory: CVE-2024-53154
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-12-24
Source: https://osv.dev/vulnerability/CVE-2024-53154
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.18.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: clk-apple-nco: Add NULL check in applnco_probe

Add NULL check in applnco_probe, to handle kernel NULL pointer
dereference error.

## References
- https://git.kernel.org/stable/c/066c14619e8379c1bafbbf8196fd38eac303472b
- https://git.kernel.org/stable/c/534e02f83889ccef5fe6beb46e773ab9d4ae1655
- https://git.kernel.org/stable/c/72ea9a7e9e260aa39f9d1c9254cf92adfb05c4f5
- https://git.kernel.org/stable/c/969c765e2b508cca9099d246c010a1e48dcfd089
- https://git.kernel.org/stable/c/9a5905b725739af6a105f9e564e7c80d69969d2b
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/53xxx/CVE-2024-53154.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-53154
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
