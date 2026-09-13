# [C] Nokogiri before 1.18.3 Stack Buffer Overflow and Use-After-Free

## Summary
Severity: Critical
Advisory: CVE-2025-71407
Aliases: GHSA-vvfq-8hwr-qm4m
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-25
Source: https://osv.dev/vulnerability/CVE-2025-71407
Type: osv

## Details
Nokogiri before 1.18.3 contains a stack buffer overflow vulnerability in libxml2 when reporting DTD validation errors with long QName prefixes, and a use-after-free vulnerability during validation against untrusted XML Schemas. Attackers can trigger these vulnerabilities by providing malicious DTD content or untrusted XSD files to cause denial of service or potential code execution.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/71xxx/CVE-2025-71407.json
- https://github.com/sparklemotion/nokogiri/security/advisories/GHSA-vvfq-8hwr-qm4m
- https://nvd.nist.gov/vuln/detail/CVE-2025-71407
- https://www.vulncheck.com/advisories/nokogiri-before-stack-buffer-overflow-and-use-after-free
