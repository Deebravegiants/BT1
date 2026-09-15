# [H] CVE-2019-6476

## Summary
Severity: High
Advisory: CVE-2019-6476
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-10-17
Source: https://osv.dev/vulnerability/CVE-2019-6476
Type: osv

## Details
A defect in code added to support QNAME minimization can cause named to exit with an assertion failure if a forwarder returns a referral rather than resolving the query. This affects BIND versions 9.14.0 up to 9.14.6, and 9.15.0 up to 9.15.4.

## References
- https://support.f5.com/csp/article/K42238532?utm_source=f5support&amp%3Butm_medium=RSS
- https://kb.isc.org/docs/cve-2019-6476
- https://security.netapp.com/advisory/ntap-20191024-0004/
