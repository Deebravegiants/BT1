# [M] CVE-2019-1010201

## Summary
Severity: Medium
Advisory: CVE-2019-1010201
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-1010201
Type: osv

## Details
Jeesite 1.2.7 is affected by: SQL Injection. The impact is: sensitive information disclosure. The component is: updateProcInsIdByBusinessId() function in src/main/java/com.thinkgem.jeesite/modules/act/ActDao.java has SQL Injection vulnerability. The attack vector is: network connectivity,authenticated. The fixed version is: 4.0 and later.

## References
- https://github.com/thinkgem/jeesite/blob/master/src/main/java/com/thinkgem/jeesite/modules/act/dao/ActDao.java
