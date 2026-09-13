# [H] CVE-2019-3569

## Summary
Severity: High
Advisory: CVE-2019-3569
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-06-26
Source: https://osv.dev/vulnerability/CVE-2019-3569
Type: osv

## Details
HHVM, when used with FastCGI, would bind by default to all available interfaces. This behavior could allow a malicious individual unintended direct access to the application, which could result in information disclosure. This issue affects versions 4.3.0, 4.4.0, 4.5.0, 4.6.0, 4.7.0, 4.8.0, versions 3.30.5 and below, and all versions in the 4.0, 4.1, and 4.2 series.

## References
- https://hhvm.com/blog/2019/06/10/hhvm-4.9.0.html
- https://github.com/facebook/hhvm/commit/97ef580ec2cca9a54da6f9bd9fdd9a455f6d74ed
