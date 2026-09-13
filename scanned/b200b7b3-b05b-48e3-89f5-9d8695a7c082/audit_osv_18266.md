# [H] CVE-2020-25690

## Summary
Severity: High
Advisory: CVE-2020-25690
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2021-02-23
Source: https://osv.dev/vulnerability/CVE-2020-25690
Type: osv

## Details
An out-of-bounds write flaw was found in FontForge in versions before 20200314 while parsing SFD files containing certain LayerCount tokens. This flaw allows an attacker to manipulate the memory allocated on the heap, causing the application to crash or execute arbitrary code. The highest threat from this vulnerability is to confidentiality, integrity, as well as system availability.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1893188
