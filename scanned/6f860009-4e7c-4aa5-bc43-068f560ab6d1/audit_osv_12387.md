# [C] CVE-2018-11652

## Summary
Severity: Critical
Advisory: CVE-2018-11652
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-06-01
Source: https://osv.dev/vulnerability/CVE-2018-11652
Type: osv

## Details
CSV Injection vulnerability in Nikto 2.1.6 and earlier allows remote attackers to inject arbitrary OS commands via the Server field in an HTTP response header, which is directly injected into a CSV report.

## References
- https://github.com/sullo/nikto/commit/e759b3300aace5314fe3d30800c8bd83c81c29f7
- https://www.exploit-db.com/exploits/44899/
