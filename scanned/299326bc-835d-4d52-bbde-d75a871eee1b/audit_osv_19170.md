# [C] CVE-2020-8443

## Summary
Severity: Critical
Advisory: CVE-2020-8443
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-01-30
Source: https://osv.dev/vulnerability/CVE-2020-8443
Type: osv

## Details
In OSSEC-HIDS 2.7 through 3.5.0, the server component responsible for log analysis (ossec-analysisd) is vulnerable to an off-by-one heap-based buffer overflow during the cleaning of crafted syslog msgs (received from authenticated remote agents and delivered to the analysisd processing queue by ossec-remoted).

## References
- https://github.com/ossec/ossec-hids/issues/1821
- https://security.gentoo.org/glsa/202007-33
- https://www.ossec.net/
- https://github.com/ossec/ossec-hids/issues/1816
