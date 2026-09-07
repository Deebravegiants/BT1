# [M] INTER-Mediator Cross-Site Scripting (XSS)

## Summary
Severity: Medium
Advisory: GHSA-w969-pq6x-267j
CVE: CVE-2017-6484
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-w969-pq6x-267j
Type: github-advisory

## Affected
- Packagist: `inter-mediator/inter-mediator` — affected >=5.5 <5.6

## Details
Multiple Cross-Site Scripting (XSS) issues were discovered in INTER-Mediator 5.5. The vulnerabilities exist due to insufficient filtration of user-supplied data (c and cred) passed to the "INTER-Mediator-master/Auth_Support/PasswordReset/resetpassword.php" URL. An attacker could execute arbitrary HTML and script code in a browser in the context of the vulnerable website.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-6484
- https://github.com/INTER-Mediator/INTER-Mediator/issues/772
- https://github.com/INTER-Mediator/INTER-Mediator
