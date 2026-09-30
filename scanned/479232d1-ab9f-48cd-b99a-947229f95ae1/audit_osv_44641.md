# [H] Integer overflow in tensor buffer validation in Deep Java Library

## Summary
Severity: High
Advisory: CVE-2026-85228
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-85228
Type: osv

## Details
An integer overflow in the tensor buffer validation component in Amazon Deep Java Library (DJL) from 0.13.0 through 0.36.0 on all platforms might allow a remote unauthenticated actor to obtain information from adjacent process memory or cause a denial of service via a crafted tensor payload.



To remediate this issue, users should upgrade to version 0.37.0 or above.

## References
- https://aws.amazon.com/security/security-bulletins/2026-106-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/85xxx/CVE-2026-85228.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-85228
- https://github.com/deepjavalibrary/djl/releases/tag/v0.37.0
