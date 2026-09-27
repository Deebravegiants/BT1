# [M] CVE-2025-25946

## Summary
Severity: Medium
Advisory: CVE-2025-25946
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-02-19
Source: https://osv.dev/vulnerability/CVE-2025-25946
Type: osv

## Details
An issue in Bento4 v1.6.0-641 allows an attacker to cause a memory leak via Ap4Marlin.cpp and Ap4Processor.cpp, specifically in AP4_MarlinIpmpEncryptingProcessor::Initialize and AP4_Processor::Process, during the execution of mp4encrypt with a specially crafted MP4 input file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25946.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-25946
- https://github.com/axiomatic-systems/Bento4/issues/994
