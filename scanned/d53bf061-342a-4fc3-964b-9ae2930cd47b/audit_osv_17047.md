# [H] CVE-2020-11709

## Summary
Severity: High
Advisory: CVE-2020-11709
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-04-12
Source: https://osv.dev/vulnerability/CVE-2020-11709
Type: osv

## Details
cpp-httplib through 0.5.8 does not filter \r\n in parameters passed into the set_redirect and set_header functions, which creates possibilities for CRLF injection and HTTP response splitting in some specific contexts.

## References
- https://gist.github.com/shouc/a9330df817128bc4c4132abf3de09495
- https://github.com/yhirose/cpp-httplib/issues/425
