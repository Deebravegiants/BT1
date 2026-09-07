# [M] cg vulnerable to an Open Redirect Vulnerability on Referer Header

## Summary
Severity: Medium
Advisory: GHSA-w228-rfpx-fhm4
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-04-23
Source: https://github.com/advisories/GHSA-w228-rfpx-fhm4
Type: github-advisory

## Affected
- PyPI: `cg` — affected >=0 <60.2.12

## Details
### Summary

A vulnerability has been discovered in the handling of the referrer header in the application, which could allow an attacker to conduct open redirects. The issue arises from improper validation of the referrer header in certain conditions. By manipulating the referrer header, an attacker could potentially redirect users to malicious websites, phishing pages, or other dangerous destinations.

### PoC

If you change the referer header, you will be redirected to that domain without verifying.

https://github.com/Clinical-Genomics/cg/blob/master/cg/server/invoices/views.py#L173

### Impact

An attacker exploiting this vulnerability could trick users into visiting malicious websites or disclose sensitive information by redirecting them to unintended destinations. This could lead to various attacks including phishing, malware distribution, or further exploitation of other vulnerabilities.

## References
- https://github.com/Clinical-Genomics/cg/security/advisories/GHSA-w228-rfpx-fhm4
- https://github.com/Clinical-Genomics/cg/commit/96e6a968a5a3639cc40ad251ad65952e4f38dd25
- https://github.com/Clinical-Genomics/cg
- https://github.com/Clinical-Genomics/cg/blob/master/cg/server/invoices/views.py#L173
