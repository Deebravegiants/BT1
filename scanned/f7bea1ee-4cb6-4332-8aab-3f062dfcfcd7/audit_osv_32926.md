# [H] software node: Correct a OOB check in software_node_get_reference_args()

## Summary
Severity: High
Advisory: CVE-2025-38342
Ecosystem: Linux
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-10
Source: https://osv.dev/vulnerability/CVE-2025-38342
Type: osv

## Affected
- Linux: `Kernel` — affected >=5.0.0 <5.10.239, >=5.11.0 <5.15.186, >=5.16.0 <6.1.142, >=6.2.0 <6.6.95, >=6.7.0 <6.12.35, >=6.13.0 <6.15.4

## Details
In the Linux kernel, the following vulnerability has been resolved:

software node: Correct a OOB check in software_node_get_reference_args()

software_node_get_reference_args() wants to get @index-th element, so
the property value requires at least '(index + 1) * sizeof(*ref)' bytes
but that can not be guaranteed by current OOB check, and may cause OOB
for malformed property.

Fix by using as OOB check '((index + 1) * sizeof(*ref) > prop->length)'.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-082556.html
- https://git.kernel.org/stable/c/142acd739eb6f08c148a96ae8309256f1422ff4b
- https://git.kernel.org/stable/c/31e4e12e0e9609850cefd4b2e1adf782f56337d6
- https://git.kernel.org/stable/c/4b3383110b6df48e0ba5936af2cb68d5eb6bd43b
- https://git.kernel.org/stable/c/56ce76e8d406cc72b89aee7931df5cf3f18db49d
- https://git.kernel.org/stable/c/7af18e42bdefe1dba5bcb32555a4d524fd504939
- https://git.kernel.org/stable/c/9324127b07dde8529222dc19233aa57ec810856c
- https://git.kernel.org/stable/c/f9397cf7bfb680799fb8c7f717c8f756384c3280
- https://lists.debian.org/debian-lts-announce/2025/10/msg00007.html
- https://lists.debian.org/debian-lts-announce/2025/10/msg00008.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/38xxx/CVE-2025-38342.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-38342
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
