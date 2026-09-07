# [M] Cross-Site Scripting in keystone

## Summary
Severity: Medium
Advisory: GHSA-7qcx-jmrc-h2rr
CVE: CVE-2017-15878
CWE: CWE-79
Ecosystem: npm
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2017-11-15
Source: https://github.com/advisories/GHSA-7qcx-jmrc-h2rr
Type: github-advisory

## Affected
- npm: `keystone` — affected >=0 <4.0.0

## Details
Versions of `keystone` prior to 4.0.0 are vulnerable to Cross-Site Scripting (XSS). The package fails to sanitize user input on the `Contact Us` page,  allowing attackers to submit contact forms with malicious JavaScript in the message field. The output is not properly encoded leading an admin that opens new inquiry to execute the arbitrary JavaScript supplied in their browser.


## Recommendation

Update to version 4.0.0 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15878
- https://github.com/keystonejs/keystone/pull/4478
- https://github.com/advisories/GHSA-7qcx-jmrc-h2rr
- https://github.com/keystonejs/keystone
- https://packetstormsecurity.com/files/144756/KeystoneJS-4.0.0-beta.5-Unauthenticated-Stored-Cross-Site-Scripting.html
- https://securelayer7.net/download/pdf/KeystoneJS-Pentest-Report-SecureLayer7.pdf
- https://www.exploit-db.com/exploits/43054
- https://www.npmjs.com/advisories/980
- http://blog.securelayer7.net/keystonejs-open-source-penetration-testing-report
- http://www.securityfocus.com/bid/101541
