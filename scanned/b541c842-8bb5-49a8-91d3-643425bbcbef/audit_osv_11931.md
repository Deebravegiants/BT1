# [C] CVE-2018-1000124

## Summary
Severity: Critical
Advisory: CVE-2018-1000124
CVSS: 10.0 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2018-03-13
Source: https://osv.dev/vulnerability/CVE-2018-1000124
Type: osv

## Details
I Librarian I-librarian version 4.8 and earlier contains a XML External Entity (XXE) vulnerability in line 154 of importmetadata.php(simplexml_load_string) that can result in an attacker reading the contents of a file and SSRF. This attack appear to be exploitable via posting xml in the Parameter form_import_textarea.

## References
- https://github.com/mkucej/i-librarian/issues/116
