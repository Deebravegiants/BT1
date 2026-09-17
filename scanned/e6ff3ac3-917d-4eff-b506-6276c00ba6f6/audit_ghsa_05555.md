# [M] Bio-Formats performs unsafe Java deserialization of attacker-controlled memoization cache files (.bfmemo) during image processing

## Summary
Severity: Medium
Advisory: GHSA-qjm3-cvp9-3jj3
CVE: CVE-2026-22187
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-07
Source: https://github.com/advisories/GHSA-qjm3-cvp9-3jj3
Type: github-advisory

## Affected
- Maven: `ome:pom-bio-formats` — affected >=0

## Details
Bio-Formats versions up to and including 8.3.0 perform unsafe Java deserialization of attacker-controlled memoization cache files (.bfmemo) during image processing. The loci.formats.Memoizer class automatically loads and deserializes memo files associated with images without validation, integrity checks, or trust enforcement. An attacker who can supply a crafted .bfmemo file alongside an image can trigger deserialization of untrusted data, which may result in denial of service, logic manipulation, or potentially remote code execution in environments where suitable gadget chains are present on the classpath.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-22187
- https://docs.openmicroscopy.org/bio-formats
- https://github.com/ome/bioformats
- https://seclists.org/fulldisclosure/2026/Jan/7
- https://www.vulncheck.com/advisories/bio-formats-memoizer-unsafe-deserialization-via-bfmemo-cache-files
