# [M] recordmcount: Fix memory leaks in the uwrite function

## Summary
Severity: Medium
Advisory: CVE-2023-53318
Ecosystem: Linux
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-09-16
Source: https://osv.dev/vulnerability/CVE-2023-53318
Type: osv

## Affected
- Linux: `Kernel` — affected >=4.4.0 <4.14.316, >=4.15.0 <4.19.284, >=4.20.0 <5.4.244, >=5.5.0 <5.10.181, >=5.11.0 <5.15.113, >=5.16.0 <6.1.30, >=6.2.0 <6.3.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

recordmcount: Fix memory leaks in the uwrite function

Common realloc mistake: 'file_append' nulled but not freed upon failure

## References
- https://git.kernel.org/stable/c/25c9b185f121812cbc215fdaa1192c6b9025b428
- https://git.kernel.org/stable/c/2d9ca5f62f2ba160ff9c9be4adf401c46c04edef
- https://git.kernel.org/stable/c/3ed95a6f6c646e8bb15c354536e0ab10e8f39c08
- https://git.kernel.org/stable/c/444ec005404cead222ebce2561a9451c9ee5ad89
- https://git.kernel.org/stable/c/895130e63c93926f07caf5db286b97bd27b81de9
- https://git.kernel.org/stable/c/bd39f68a309a947670379bf9a39b16c584f86ddb
- https://git.kernel.org/stable/c/fa359d068574d29e7d2f0fdd0ebe4c6a12b5cfb9
- https://git.kernel.org/stable/c/ff70ad9159fbb566b2c15724f44207e8deccd527
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/53xxx/CVE-2023-53318.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-53318
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
