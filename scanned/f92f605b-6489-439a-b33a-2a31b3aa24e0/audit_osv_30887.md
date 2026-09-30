# [H] crypto: bcm - add error check in the ahash_hmac_init function

## Summary
Severity: High
Advisory: CVE-2024-56681
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-28
Source: https://osv.dev/vulnerability/CVE-2024-56681
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.11.0 <4.19.325, >=4.20.0 <5.4.287, >=5.5.0 <5.10.231, >=5.11.0 <5.15.174, >=5.16.0 <6.1.120, >=6.2.0 <6.6.64, >=6.7.0 <6.11.11, >=6.12.0 <6.12.2

## Details
In the Linux kernel, the following vulnerability has been resolved:

crypto: bcm - add error check in the ahash_hmac_init function

The ahash_init functions may return fails. The ahash_hmac_init should
not return ok when ahash_init returns error. For an example, ahash_init
will return -ENOMEM when allocation memory is error.

## References
- https://git.kernel.org/stable/c/05f0a3f5477ecaa1cf46448504afe9e7c2e96fcc
- https://git.kernel.org/stable/c/19630cf57233e845b6ac57c9c969a4888925467b
- https://git.kernel.org/stable/c/28f8ffa945f7d7150463e15097ea73b19529d6f5
- https://git.kernel.org/stable/c/4ea3e3b761e371102bb1486778e2f8dbc9e37413
- https://git.kernel.org/stable/c/75e1e38e5d80d6d9011b7322698ffba3dd3db30a
- https://git.kernel.org/stable/c/8f1a9a960b1107bd0e0ec3736055f5ed0e717edf
- https://git.kernel.org/stable/c/ae5253313e0ea5f00c06176074592b7f493c8546
- https://git.kernel.org/stable/c/bba9e38c5ad41d0a88b22a59e5b6dd3e31825118
- https://git.kernel.org/stable/c/ee36db8e8203420e6d5c42eb9428920c2fc36532
- https://lists.debian.org/debian-lts-announce/2025/03/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/56xxx/CVE-2024-56681.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-56681
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
