# [C] Use of Insufficiently Random Values in penggle:kaptcha

## Summary
Severity: Critical
Advisory: GHSA-8q89-pwhh-7wfq
CVE: CVE-2018-18531
CWE: CWE-330
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-10-23
Source: https://github.com/advisories/GHSA-8q89-pwhh-7wfq
Type: github-advisory

## Affected
- Maven: `com.github.penggle:kaptcha` — affected >=0

## Details
text/impl/DefaultTextCreator.java, text/impl/ChineseTextProducer.java, and text/impl/FiveLetterFirstNameTextCreator.java in kaptcha 2.3.2 use the Random (rather than SecureRandom) function for generating CAPTCHA values, which makes it easier for remote attackers to bypass intended access restrictions via a brute-force approach.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-18531
- https://github.com/penggle/kaptcha/issues/3
- https://github.com/advisories/GHSA-8q89-pwhh-7wfq
- https://github.com/penggle/kaptcha
