# [M] Nokogiri before 1.19.4 Invalid Memory Read via initialize_copy_with_args

## Summary
Severity: Medium
Advisory: CVE-2026-79769
Aliases: GHSA-g9g8-vgvw-g3vf
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2026-79769
Type: osv

## Details
Nokogiri versions before 1.19.4 contain a possible invalid (out-of-bounds) memory read in the protected internal Node#initialize_copy_with_args helper behind Node#dup and #clone, which unwrapped its source argument as an xmlNode without a type check. If application code calls this protected method with a non-Node argument (e.g., a Namespace), it reads an xmlNs out of bounds, crashing the process. This is only triggerable by a programming error and cannot be triggered by untrusted input or normal use of the public API. Only CRuby is affected. Version 1.19.4 adds a type check and raises TypeError.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/79xxx/CVE-2026-79769.json
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-g9g8-vgvw-g3vf
- https://nvd.nist.gov/vuln/detail/CVE-2026-79769
- https://www.vulncheck.com/advisories/nokogiri-before-invalid-memory-read-via-initialize-copy-with-args
