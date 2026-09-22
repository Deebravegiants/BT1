# [M] CVE-2019-10180

## Summary
Severity: Medium
Advisory: CVE-2019-10180
CVSS: 4.8 (CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-03-31
Source: https://osv.dev/vulnerability/CVE-2019-10180
Type: osv

## Details
A vulnerability was found in all pki-core 10.x.x version, where the Token Processing Service (TPS) did not properly sanitize several parameters stored for the tokens, possibly resulting in a Stored Cross Site Scripting (XSS) vulnerability. An attacker able to modify the parameters of any token could use this flaw to trick an authenticated user into executing arbitrary JavaScript code.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10180
