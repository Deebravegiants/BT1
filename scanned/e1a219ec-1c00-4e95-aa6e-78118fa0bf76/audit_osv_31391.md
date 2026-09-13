# [M] Heap Buffer overflow in Abseil

## Summary
Severity: Medium
Advisory: CVE-2025-0838
CVSS: 6.0 (CVSS:4.0/AV:A/AC:H/AT:P/PR:L/UI:A/VC:L/VI:H/VA:L/SC:L/SI:H/SA:L)
Published: 2025-02-21
Source: https://osv.dev/vulnerability/CVE-2025-0838
Type: osv

## Details
There exists a heap buffer overflow vulnerable in Abseil-cpp. The sized constructors, reserve(), and rehash() methods of absl::{flat,node}hash{set,map} did not impose an upper bound on their size argument. As a result, it was possible for a caller to pass a very large size that would cause an integer overflow when computing the size of the container's backing store, and a subsequent out-of-bounds memory write. Subsequent accesses to the container might also access out-of-bounds memory. We recommend upgrading past commit 5a0e2cb5e3958dd90bb8569a2766622cb74d90c1

## References
- https://lists.debian.org/debian-lts-announce/2025/04/msg00012.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/0xxx/CVE-2025-0838.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-0838
- https://github.com/abseil/abseil-cpp/commit/5a0e2cb5e3958dd90bb8569a2766622cb74d90c1
- https://github.com/abseil/abseil-cpp
