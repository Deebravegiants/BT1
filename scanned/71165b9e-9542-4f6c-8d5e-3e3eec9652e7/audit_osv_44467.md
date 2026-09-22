# [M] Identity tool filter in AshAi accepts operator maps, allowing update or destroy of unidentified records

## Summary
Severity: Medium
Advisory: CVE-2026-82564
Aliases: EEF-CVE-2026-82564, GHSA-jg86-xh36-h5xc
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-31
Source: https://osv.dev/vulnerability/CVE-2026-82564
Type: osv

## Details
Authorization Bypass Through User-Controlled Key vulnerability in ash-project ash_ai allows a caller of an identity-configured tool to update or destroy records it never identified, including every row in the table.

In AshAi.Tool.Execution, identity_filter/3 built the update/destroy filter directly from the raw tool arguments as [{key, Map.get(arguments, to_string(key))}] and passed it to Ash.Query.do_filter/2. A map value is parsed as a predicate expression rather than a literal, so a caller can send {"public_ref": {"not_eq": "<own-ref>"}} and, combined with Ash.Query.limit(1) and Ash.bulk_update!/Ash.bulk_destroy!, retarget the write at a record it never identified; an omitted key yields an IS NULL filter that matches an arbitrary row. The fix casts each identity value to the field type, rejecting non-scalar inputs.

This issue affects ash_ai: from 0.6.0 before 1.0.0.

## References
- https://cna.erlef.org/cves/CVE-2026-82564.html
- https://github.com
- https://osv.dev/vulnerability/EEF-CVE-2026-82564
- https://repo.hex.pm
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/82xxx/CVE-2026-82564.json
- https://github.com/ash-project/ash_ai/security/advisories/GHSA-jg86-xh36-h5xc
- https://nvd.nist.gov/vuln/detail/CVE-2026-82564
- https://github.com/ash-project/ash_ai/commit/87f616d5bfbf7af43346f0701ae17f853789a602
- https://github.com/ash-project/ash_ai
