# [M] CVE-2021-47052

## Summary
Severity: Medium
Advisory: CVE-2021-47052
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2021-47052
Type: osv

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: sa2ul - Fix memory leak of rxd

There are two error return paths that are not freeing rxd and causing
memory leaks.  Fix these.

Addresses-Coverity: ("Resource leak")

## References
- https://git.kernel.org/stable/c/0e596b3734649041ed77edc86a23c0442bbe062b
- https://git.kernel.org/stable/c/854b7737199848a91f6adfa0a03cf6f0c46c86e8
- https://git.kernel.org/stable/c/b7bd0657c2036add71981d88a7fae50188150b6e
- https://git.kernel.org/stable/c/dfd6443bf49ac17adf882ca46c40c506a0284bd6
