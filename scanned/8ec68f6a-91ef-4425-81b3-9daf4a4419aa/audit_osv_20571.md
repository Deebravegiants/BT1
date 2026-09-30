# [H] CVE-2021-3529

## Summary
Severity: High
Advisory: CVE-2021-3529
CVSS: 7.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:L)
Published: 2021-06-02
Source: https://osv.dev/vulnerability/CVE-2021-3529
Type: osv

## Details
A flaw was found in noobaa-core in versions before 5.7.0. This flaw results in the name of an arbitrarily URL being copied into an HTML document as plain text between tags, including potentially a payload script. The input was echoed unmodified in the application response, resulting in arbitrary JavaScript being injected into an application's response. The highest threat to the system is for confidentiality, availability, and integrity.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1950479
