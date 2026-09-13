# [M] CVE-2021-38707

## Summary
Severity: Medium
Advisory: CVE-2021-38707
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N)
Published: 2021-09-07
Source: https://osv.dev/vulnerability/CVE-2021-38707
Type: osv

## Details
Persistent cross-site scripting (XSS) vulnerabilities in ClinicCases 7.3.3 allow low-privileged attackers to introduce arbitrary JavaScript to account parameters. The XSS payloads will execute in the browser of any user who views the relevant content. This can result in account takeover via session token theft.

## References
- https://github.com/judsonmitchell/ClinicCases/releases
- https://github.com/sudonoodle/CVE-2021-38707
