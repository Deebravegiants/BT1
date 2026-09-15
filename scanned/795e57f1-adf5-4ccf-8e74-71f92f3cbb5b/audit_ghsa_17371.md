# [M] step-ca Has Improper Authorization Check for SSH Certificate Revocation

## Summary
Severity: Medium
Advisory: GHSA-j7c9-79x7-8hpr
CVE: CVE-2025-66406
CWE: CWE-285, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:L/A:H (CVSS_V3)
Published: 2025-12-03
Source: https://github.com/advisories/GHSA-j7c9-79x7-8hpr
Type: github-advisory

## Affected
- Go: `github.com/smallstep/certificates` — affected >=0 <0.29.0

## Details
## Summary
An authorized attacker can bypass authorization checks and revoke any SSH certificate issued by Step CA by using a valid revocation token.

## Details
Step CA users can obtain SSH certificates from a few provisioners. The SSHPOP provisioner allows revocation of the SSH certificate (preventing future certificate renewals) using a token. Due to a missing validity check, this token could be used to revoke any SSH certificate issued by the CA.

To create a token, an attacker must have access to the CA endpoint and a valid SSH certificate, meaning they were already authorized to obtain an SSH certificate. The attacker must also know the serial number of the certificate they want to revoke.

## Impact
There is no way to mitigate this attack. It is recommended to update to v0.29.0 or newer.

## Fix
In v0.29.0, the token validation logic was strengthened to bind each token to a specific SSH certificate serial number.

## Acknowledgements
This issue was identified and reported by Gabriel Departout and Andy Russon, from [AMOSSYS](http://amossys.fr/). This audit was sponsored by [ANSSI](https://cyber.gouv.fr/) (French Cybersecurity Agency) based on [their Open-Source security audit program](https://cyber.gouv.fr/open-source-lanssi#:~:text=Financement%20d%27%C3%A9valuations%20de%20s%C3%A9curit%C3%A9%20de%20logiciels%20libres).

## Embargo List

If your organization runs Step CA in production and would like advance, embargoed notification of future security updates, visit https://u.step.sm/disclosure to request inclusion on our embargo list.

Stay safe, and thank you for helping us keep the ecosystem secure.

## References
- https://github.com/smallstep/certificates/security/advisories/GHSA-j7c9-79x7-8hpr
- https://nvd.nist.gov/vuln/detail/CVE-2025-66406
- https://github.com/smallstep/certificates
