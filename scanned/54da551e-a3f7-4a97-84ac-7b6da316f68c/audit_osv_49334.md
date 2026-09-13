# [M] CVE-2019-10178

## Summary
Severity: Medium
Advisory: CVE-2019-10178
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2020-03-18
Source: https://osv.dev/vulnerability/CVE-2019-10178
Type: osv

## Details
It was found that the Token Processing Service (TPS) did not properly sanitize the Token IDs from the "Activity" page, enabling a Stored Cross Site Scripting (XSS) vulnerability. An unauthenticated attacker could trick an authenticated victim into creating a specially crafted activity, which would execute arbitrary JavaScript code when viewed in a browser. All versions of pki-core are believed to be vulnerable.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2019-10178
