# [C] fou: fix initialization of grc

## Summary
Severity: Critical
Advisory: CVE-2024-46865
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-09-27
Source: https://osv.dev/vulnerability/CVE-2024-46865
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.10.226 <5.10.227, >=5.15.167 <5.15.168, >=6.1.110 <6.1.111, >=6.6.51 <6.6.52, >=6.10.10 <6.10.11

## Details
In the Linux kernel, the following vulnerability has been resolved:

fou: fix initialization of grc

The grc must be initialize first. There can be a condition where if
fou is NULL, goto out will be executed and grc would be used
uninitialized.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://git.kernel.org/stable/c/16ff0895283058b0f96d4fe277aa25ee096f0ea8
- https://git.kernel.org/stable/c/392f6a97fcbecc64f0c00058b2db5bb0e4b8cc3e
- https://git.kernel.org/stable/c/4c8002277167125078e6b9b90137bdf443ebaa08
- https://git.kernel.org/stable/c/5d537b8d900514509622ce92330b70d2e581d409
- https://git.kernel.org/stable/c/7ae890ee19479eeeb87724cca8430b5cb3660c74
- https://git.kernel.org/stable/c/aca06c617c83295f0caa486ad608fbef7bdc11e8
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://lists.debian.org/debian-lts-announce/2025/03/msg00002.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/46xxx/CVE-2024-46865.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-46865
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
