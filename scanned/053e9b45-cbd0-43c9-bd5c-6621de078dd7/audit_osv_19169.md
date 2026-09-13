# [H] CVE-2020-8442

## Summary
Severity: High
Advisory: CVE-2020-8442
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-30
Source: https://osv.dev/vulnerability/CVE-2020-8442
Type: osv

## Details
In OSSEC-HIDS 2.7 through 3.5.0, the server component responsible for log analysis (ossec-analysisd) is vulnerable to a heap-based buffer overflow in the rootcheck decoder component via an authenticated client.

## References
- https://github.com/ossec/ossec-hids/issues/1821
- https://security.gentoo.org/glsa/202007-33
- https://www.ossec.net/
- https://github.com/ossec/ossec-hids/issues/1820
