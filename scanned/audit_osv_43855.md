# [M] cgltf 1.15 Integer Overflow via cgltf_validate() Accessor Bounds Check

## Summary
Severity: Medium
Advisory: CVE-2026-75148
CVSS: 6.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:P/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-19
Source: https://osv.dev/vulnerability/CVE-2026-75148
Type: osv

## Details
cgltf through 1.15 contains an integer overflow vulnerability in the non-sparse accessor bounds check within cgltf_validate() that allows remote attackers to cause memory disclosure and denial of service by supplying crafted accessor count values. Attackers can provide malformed .gltf or .glb input with a specially crafted accessor count to overflow the unsigned integer multiplication of accessor stride and element count, causing the bounds check to pass and triggering a heap out-of-bounds read when cgltf_accessor_read_float() is subsequently called on the validated malformed accessor.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75148.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-75148
- https://www.vulncheck.com/advisories/cgltf-integer-overflow-via-cgltf-validate-accessor-bounds-check
- https://github.com/jkuhlmann/cgltf/issues/301
- https://github.com/jkuhlmann/cgltf
