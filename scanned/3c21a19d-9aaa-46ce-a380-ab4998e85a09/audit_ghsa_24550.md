# [H] Cross-Site Request Forgery in hawtio

## Summary
Severity: High
Advisory: GHSA-q4q2-fvwf-6ghv
CVE: CVE-2017-7556
CWE: CWE-352
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-q4q2-fvwf-6ghv
Type: github-advisory

## Affected
- Maven: `io.hawt:project` — affected >=0 <1.5.4

## Details
It was found that hawtio contains a CSRF flaw that allows unrelated websites to perform actions as the authenticated user. Attackers could use this vulnerability to trick the user to visit his website that contains a malicious script which can be submitted to hawtio server on behalf of the user.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7556
- https://bugzilla.redhat.com/show_bug.cgi?id=1480060
- https://github.com/hawtio/hawtio
