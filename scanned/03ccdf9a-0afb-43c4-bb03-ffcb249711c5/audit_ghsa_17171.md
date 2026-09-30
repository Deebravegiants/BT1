# [M] aiosmtpd vulnerable to SMTP smuggling

## Summary
Severity: Medium
Advisory: GHSA-pr2m-px7j-xg65
CVE: CVE-2024-27305
CWE: CWE-345
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2024-03-13
Source: https://github.com/advisories/GHSA-pr2m-px7j-xg65
Type: github-advisory

## Affected
- PyPI: `aiosmtpd` — affected >=0 <1.4.5

## Details
### Summary
aiosmtpd is vulnerable to inbound SMTP smuggling. SMTP smuggling is a novel vulnerability based on not so novel interpretation differences of the SMTP protocol. By exploiting SMTP smuggling, an attacker may send smuggle/spoof e-mails with fake sender addresses, allowing advanced phishing attacks. This issue also existed in other SMTP software like Postfix (https://www.postfix.org/smtp-smuggling.html).

### Details
Detailed information on SMTP smuggling can be found in the full blog post (https://sec-consult.com/blog/detail/smtp-smuggling-spoofing-e-mails-worldwide/) or on the Postfix homepage (https://www.postfix.org/smtp-smuggling.html). (and soon on the official website https://smtpsmuggling.com/)  

### Impact
With the right SMTP server constellation, an attacker can send spoofed e-mails to inbound/receiving aiosmtpd instances.

## References
- https://github.com/aio-libs/aiosmtpd/security/advisories/GHSA-pr2m-px7j-xg65
- https://nvd.nist.gov/vuln/detail/CVE-2024-27305
- https://github.com/aio-libs/aiosmtpd/commit/24b6c79c8921cf1800e27ca144f4f37023982bbb
- https://github.com/aio-libs/aiosmtpd
- https://github.com/pypa/advisory-database/tree/main/vulns/aiosmtpd/PYSEC-2024-221.yaml
- https://www.postfix.org/smtp-smuggling.html
