# [H] CVE-2018-7466

## Summary
Severity: High
Advisory: CVE-2018-7466
CVSS: 7.5 (CVSS:3.0/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-02-25
Source: https://osv.dev/vulnerability/CVE-2018-7466
Type: osv

## Details
install/installNewDB.php in TestLink through 1.9.16 allows remote attackers to conduct injection attacks by leveraging control over DB LOGIN NAMES data during installation to provide a long, crafted value.

## References
- https://github.com/TestLinkOpenSourceTRMS/testlink-code/commit/9696012eecbafb0aa21cc346234512c29b474679
- https://www.exploit-db.com/exploits/44226/
- https://www.exploit-db.com/exploits/44349/
