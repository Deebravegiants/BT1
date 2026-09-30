# [M] Memory-amplification denial of service via declared-length preallocation in Amazon ion-java

## Summary
Severity: Medium
Advisory: CVE-2026-75935
Aliases: GHSA-822f-6gg9-whr5
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-08-18
Source: https://osv.dev/vulnerability/CVE-2026-75935
Type: osv

## Details
Uncontrolled memory allocation in the binary Ion stream cursor in Amazon ion-java before 1.12.0 might allow remote actors to cause a denial of service via a crafted Ion binary document containing a declared-length field that causes excessive heap preallocation.



To remediate this issue, users should upgrade to version 1.12.0.

## References
- https://aws.amazon.com/security/security-bulletins/2026-083-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75935.json
- https://github.com/amazon-ion/ion-java/security/advisories/GHSA-822f-6gg9-whr5
- https://nvd.nist.gov/vuln/detail/CVE-2026-75935
- https://github.com/amazon-ion/ion-java/releases/tag/v1.12.0
