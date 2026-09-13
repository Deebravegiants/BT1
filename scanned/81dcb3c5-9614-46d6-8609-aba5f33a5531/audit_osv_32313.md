# [M] Denial of Service (DoS) in WeGIA due to Recursive Crawling of Dynamic URLs

## Summary
Severity: Medium
Advisory: CVE-2025-27419
Aliases: GHSA-9rp6-4mqp-g4p8
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H)
Published: 2025-03-03
Source: https://osv.dev/vulnerability/CVE-2025-27419
Type: osv

## Details
WeGIA is an open source Web Manager for Institutions with a focus on Portuguese language users. A Denial of Service (DoS) vulnerability exists in WeGIA. This vulnerability allows any unauthenticated user to cause the server to become unresponsive by performing aggressive spidering. The vulnerability is caused by recursive crawling of dynamically generated URLs and insufficient handling of large volumes of requests. This vulnerability is fixed in 3.2.16.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27419.json
- https://github.com/LabRedesCefetRJ/WeGIA/security/advisories/GHSA-9rp6-4mqp-g4p8
- https://nvd.nist.gov/vuln/detail/CVE-2025-27419
- https://github.com/LabRedesCefetRJ/WeGIA/commit/624ddfadb3fd8f8b30ad4f601b032a9bacc86a39
