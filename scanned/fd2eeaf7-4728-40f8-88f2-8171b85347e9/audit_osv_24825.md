# [M] CVE-2023-27293

## Summary
Severity: Medium
Advisory: CVE-2023-27293
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2023-02-28
Source: https://osv.dev/vulnerability/CVE-2023-27293
Type: osv

## Details
Improper neutralization of input during web page generation allows an unauthenticated attacker to submit malicious Javascript as the answer to a questionnaire which would then be executed when an authenticated user reviews the candidate's submission. This could be used to steal other users’ cookies and force users to make actions without their knowledge.

## References
- https://www.tenable.com/security/research/tra-2023-8
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/27xxx/CVE-2023-27293.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-27293
