# [M] CVE-2019-1010202

## Summary
Severity: Medium
Advisory: CVE-2019-1010202
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2019-07-23
Source: https://osv.dev/vulnerability/CVE-2019-1010202
Type: osv

## Details
Jeesite 1.2.7 is affected by: XML External Entity (XXE). The impact is: sensitive information disclosure. The component is: convertToModel() function in src/main/java/com.thinkgem.jeesite/modules/act/service/ActProcessService.java. The attack vector is: network connectivity,authenticated,must upload a specially crafted xml file. The fixed version is: 4.0 and later.

## References
- https://github.com/thinkgem/jeesite/blob/master/src/main/java/com/thinkgem/jeesite/modules/act/service/ActProcessService.java
