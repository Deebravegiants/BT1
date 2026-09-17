# [M] clk: mediatek: Fix memory leaks on probe

## Summary
Severity: Medium
Advisory: CVE-2022-49108
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49108
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.15.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

clk: mediatek: Fix memory leaks on probe

Handle the error branches to free memory where required.

Addresses-Coverity-ID: 1491825 ("Resource leak")

## References
- https://git.kernel.org/stable/c/02742d1d5c95cff8b6e9379aae4ab12674f7265d
- https://git.kernel.org/stable/c/7a688c91d3fd54c53e7a9edd6052cdae98dd99d8
- https://git.kernel.org/stable/c/c6a0b413398588fc2d8b174a79ea715b66413fca
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49108.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49108
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
