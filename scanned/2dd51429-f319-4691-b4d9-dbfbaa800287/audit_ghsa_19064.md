# [M] OneUptime is Vulnerable to Privilege Escalation via Login Response Manipulation 

## Summary
Severity: Medium
Advisory: GHSA-675q-66gf-gqg8
CVE: CVE-2025-66028
CWE: CWE-284, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-675q-66gf-gqg8
Type: github-advisory

## Affected
- npm: `@oneuptime/common` — affected >=0 <8.0.5567

## Details
### Summary

During the login process, the server response included a parameter called isMasterAdmin. By intercepting and modifying this parameter value from false to true, a user is able to gain access to the admin dashboard interface.  However, despite accessing the admin panel, the user does not have sufficient permissions to view or interact with actual data. 


### PoC
Intercept the login response and change "isMasterAdmin": false → "isMasterAdmin": true 
<img width="1405" height="567" alt="image" src="https://github.com/user-attachments/assets/7036398b-bb41-46c1-b66a-e49ec2bc3abb" />
<img width="1533" height="476" alt="2" src="https://github.com/user-attachments/assets/4efcaef5-a939-4729-be43-3af62a7d02f8" />


### Impact
The admin dashboard is viewable.

## References
- https://github.com/OneUptime/oneuptime/security/advisories/GHSA-675q-66gf-gqg8
- https://nvd.nist.gov/vuln/detail/CVE-2025-66028
- https://github.com/OneUptime/oneuptime/commit/3e72b2a9a4f50f98cf1f6cf13fa3e405715bb370
- https://github.com/OneUptime/oneuptime
