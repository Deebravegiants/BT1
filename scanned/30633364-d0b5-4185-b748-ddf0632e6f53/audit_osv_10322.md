# [M] CVE-2017-14955

## Summary
Severity: Medium
Advisory: CVE-2017-14955
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-10-02
Source: https://osv.dev/vulnerability/CVE-2017-14955
Type: osv

## Details
Check_MK before 1.2.8p26 mishandles certain errors within the failed-login save feature because of a race condition, which allows remote attackers to obtain sensitive user information by reading a GUI crash report.

## References
- http://mathias-kettner.com/check_mk_werks.php?edition_id=raw&branch=1.2.8
- https://mathias-kettner.de/check_mk_werks.php?werk_id=5208&HTML=yes
- https://www.exploit-db.com/exploits/43021/
