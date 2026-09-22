# [M] Incomplete fix for CVE-2026-75936 memory-amplification denial of service in Amazon ion-java

## Summary
Severity: Medium
Advisory: CVE-2026-85786
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-04
Source: https://osv.dev/vulnerability/CVE-2026-85786
Type: osv

## Details
Improper handling of highly compressed data in Amazon ion-java before 1.12.1 might allow remote attackers to cause a denial of service via a crafted compressed Ion document that expands to an arbitrarily large size upon decompression due to insufficient coverage of the GZIP auto-decompression opt-out introduced for CVE-2026-75936.



To remediate this issue, users should upgrade to version 1.12.1.

## References
- https://aws.amazon.com/security/security-bulletins/2026-100-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85786.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85786
- https://github.com/amazon-ion/ion-java/releases/tag/v1.12.1
