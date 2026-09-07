# [M] Improper Neutralization of Input During Web Page Generation in Dojo Dojo Objective Harness

## Summary
Severity: Medium
Advisory: GHSA-vmq9-cm7m-4p8p
CVE: CVE-2018-1000665
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vmq9-cm7m-4p8p
Type: github-advisory

## Affected
- Maven: `org.dojotoolkit:dojo` — affected >=0 <1.14

## Details
Dojo Dojo Objective Harness (DOH) version prior to version 1.14 contains a Cross Site Scripting (XSS) vulnerability in `unit.html` and `testsDOH/_base/loader/i18n-exhaustive/i18n-test/unit.html` and `testsDOH/_base/i18nExhaustive.js` in the DOH that can result in Victim attacked through their browser - deliver malware, steal HTTP cookies, bypass CORS trust. This attack appear to be exploitable via Victims are typically lured to a web site under the attacker's control; the XSS vulnerability on the target domain is silently exploited without the victim's knowledge. This vulnerability appears to have been fixed in 1.14.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-1000665
- https://github.com/dojo/dojo/pull/307
- https://dojotoolkit.org/blog/dojo-1-14-released
- https://github.com/dojo/dojo
