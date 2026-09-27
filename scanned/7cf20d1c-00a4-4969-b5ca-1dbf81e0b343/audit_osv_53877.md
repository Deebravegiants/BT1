# [C] CVE-2023-29827

## Summary
Severity: Critical
Advisory: CVE-2023-29827
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-04
Source: https://osv.dev/vulnerability/CVE-2023-29827
Type: osv

## Details
ejs v3.1.9 is vulnerable to server-side template injection. If the ejs file is controllable, template injection can be implemented through the configuration settings of the closeDelimiter parameter. NOTE: this is disputed by the vendor because the render function is not intended to be used with untrusted input.

## References
- https://github.com/mde/ejs/blob/main/SECURITY.md#out-of-scope-vulnerabilities
- https://github.com/mde/ejs/issues/720
