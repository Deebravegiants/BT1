# [M] Bluetooth: use memset avoid memory leaks

## Summary
Severity: Medium
Advisory: CVE-2022-49116
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-26
Source: https://osv.dev/vulnerability/CVE-2022-49116
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.7.0 <5.10.111, >=5.11.0 <5.15.34, >=5.16.0 <5.16.20, >=5.17.0 <5.17.3

## Details
In the Linux kernel, the following vulnerability has been resolved:

Bluetooth: use memset avoid memory leaks

Use memset to initialize structs to prevent memory leaks
in l2cap_ecred_connect

## References
- https://git.kernel.org/stable/c/42b6a39f439b6f37cc2024d91ce547d83290ff78
- https://git.kernel.org/stable/c/9567d54e70ff58c2695c2cc2e53c86c67551d3e6
- https://git.kernel.org/stable/c/d3715b2333e9a21692ba16ef8645eda584a9515d
- https://git.kernel.org/stable/c/d588c183a971b85c775ad66da563ee6e8bc8158f
- https://git.kernel.org/stable/c/e9e55acee9b7a737ec7f5161b94a78932a5514c8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/49xxx/CVE-2022-49116.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-49116
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
