# [H] ACPICA: Revert "ACPICA: avoid Info: mapping multiple BARs. Your kernel is fine."

## Summary
Severity: High
Advisory: CVE-2024-40984
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-07-12
Source: https://osv.dev/vulnerability/CVE-2024-40984
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.32 <4.19.317, >=4.20.0 <5.4.279, >=5.5.0 <5.10.221, >=5.11.0 <5.15.162, >=5.16.0 <6.1.96, >=6.2.0 <6.6.36, >=6.7.0 <6.9.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

ACPICA: Revert "ACPICA: avoid Info: mapping multiple BARs. Your kernel is fine."

Undo the modifications made in commit d410ee5109a1 ("ACPICA: avoid
"Info: mapping multiple BARs. Your kernel is fine.""). The initial
purpose of this commit was to stop memory mappings for operation
regions from overlapping page boundaries, as it can trigger warnings
if different page attributes are present.

However, it was found that when this situation arises, mapping
continues until the boundary's end, but there is still an attempt to
read/write the entire length of the map, leading to a NULL pointer
deference. For example, if a four-byte mapping request is made but
only one byte is mapped because it hits the current page boundary's
end, a four-byte read/write attempt is still made, resulting in a NULL
pointer deference.

Instead, map the entire length, as the ACPI specification does not
mandate that it must be within the same page boundary. It is
permissible for it to be mapped across different regions.

## References
- https://cert-portal.siemens.com/productcert/html/ssa-265688.html
- https://cert-portal.siemens.com/productcert/html/ssa-355557.html
- https://cert-portal.siemens.com/productcert/html/ssa-613116.html
- https://git.kernel.org/stable/c/434c6b924e1f4c219aab2d9e05fe79c5364e37d3
- https://git.kernel.org/stable/c/435ecc978c3d5d0c4e172ec5b956dc1904061d98
- https://git.kernel.org/stable/c/6eca23100e9030725f69c1babacd58803f29ec8d
- https://git.kernel.org/stable/c/a83e1385b780d41307433ddbc86e3c528db031f0
- https://git.kernel.org/stable/c/ae465109d82f4fb03c5adbe85f2d6a6a3d59124c
- https://git.kernel.org/stable/c/dc5017c57f5eee80020c73ff8b67ba7f9fd08b1f
- https://git.kernel.org/stable/c/ddc1f5f124479360a1fd43f73be950781d172239
- https://git.kernel.org/stable/c/e21a4c9129c72fa54dd00f5ebf71219b41d43c04
- https://lists.debian.org/debian-lts-announce/2025/01/msg00001.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/40xxx/CVE-2024-40984.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-40984
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
