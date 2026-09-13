# [H] CVE-2021-3584

## Summary
Severity: High
Advisory: CVE-2021-3584
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-12-23
Source: https://osv.dev/vulnerability/CVE-2021-3584
Type: osv

## Details
A server side remote code execution vulnerability was found in Foreman project. A authenticated attacker could use Sendmail configuration options to overwrite the defaults and perform command injection. The highest threat from this vulnerability is to confidentiality, integrity and availability of system. Fixed releases are 2.4.1, 2.5.1, 3.0.0.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1968439
- https://github.com/theforeman/foreman/pull/8599
- https://projects.theforeman.org/issues/32753
