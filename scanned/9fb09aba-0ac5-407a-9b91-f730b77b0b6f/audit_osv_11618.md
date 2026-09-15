# [H] CVE-2017-9080

## Summary
Severity: High
Advisory: CVE-2017-9080
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-19
Source: https://osv.dev/vulnerability/CVE-2017-9080
Type: osv

## Details
PlaySMS 1.4 allows remote code execution because PHP code in the name of an uploaded .php file is executed. sendfromfile.php has a combination of Unrestricted File Upload and Code Injection.

## References
- http://touhidshaikh.com/blog/poc/playsms-v1-4-rce/
- https://www.exploit-db.com/exploits/42003/
- https://www.exploit-db.com/exploits/44599/
