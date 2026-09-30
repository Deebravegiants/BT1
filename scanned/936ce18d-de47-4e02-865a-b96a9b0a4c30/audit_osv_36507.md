# [M] Denial of Service via Oversized Package Upload

## Summary
Severity: Medium
Advisory: CVE-2026-23940
Aliases: EEF-CVE-2026-23940, GHSA-jp8w-gxf6-8hcr
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-03-13
Source: https://osv.dev/vulnerability/CVE-2026-23940
Type: osv

## Details
Uncontrolled Resource Consumption vulnerability in hexpm hexpm/hexpm allows Excessive Allocation.

Publishing an oversized package can cause Hex.pm to run out of memory while extracting the uploaded package tarball. This can terminate the affected application instance and result in a denial of service for package publishing and potentially other package-processing functionality.

This issue affects hex.pm: before 2026-03-10.

## References
- https://cna.erlef.org/cves/CVE-2026-23940.html
- https://github.com
- https://hex.pm
- https://osv.dev/vulnerability/EEF-CVE-2026-23940
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/23xxx/CVE-2026-23940.json
- https://github.com/hexpm/hexpm/security/advisories/GHSA-jp8w-gxf6-8hcr
- https://nvd.nist.gov/vuln/detail/CVE-2026-23940
- https://github.com/hexpm/hexpm/commit/495f01607d3eae4aed7ad09b2f54f31ec7a7df01
- https://github.com/hexpm/hexpm/commit/82911daf5f8fb2ab44f298e3ba22b90bc1ae3746
- https://github.com/hexpm/hexpm
