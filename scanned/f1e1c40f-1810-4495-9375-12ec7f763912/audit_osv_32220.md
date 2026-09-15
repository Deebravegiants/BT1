# [H] CVE-2025-25944

## Summary
Severity: High
Advisory: CVE-2025-25944
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-02-19
Source: https://osv.dev/vulnerability/CVE-2025-25944
Type: osv

## Details
Buffer Overflow vulnerability in Bento4 v.1.6.0-641 allows a local attacker to execute arbitrary code via the Ap4RtpAtom.cpp, specifically in AP4_RtpAtom::AP4_RtpAtom, during the execution of mp4fragment with a crafted MP4 input file.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25944.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-25944
- https://github.com/axiomatic-systems/Bento4/issues/993
