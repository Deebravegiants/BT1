# [H] CVE-2021-45102

## Summary
Severity: High
Advisory: CVE-2021-45102
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-16
Source: https://osv.dev/vulnerability/CVE-2021-45102
Type: osv

## Details
An issue was discovered in HTCondor 9.0.x before 9.0.4 and 9.1.x before 9.1.2. When authenticating to an HTCondor daemon using a SciToken, a user may be granted authorizations beyond what the token should allow.

## References
- https://research.cs.wisc.edu/htcondor/security/vulnerabilities/HTCONDOR-2021-0004/
