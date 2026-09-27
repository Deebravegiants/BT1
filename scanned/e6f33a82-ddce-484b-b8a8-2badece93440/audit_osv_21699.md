# [C] CVE-2021-45456

## Summary
Severity: Critical
Advisory: CVE-2021-45456
Aliases: GHSA-hw3m-8h25-8frw
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-01-06
Source: https://osv.dev/vulnerability/CVE-2021-45456
Type: osv

## Details
Apache kylin checks the legitimacy of the project before executing some commands with the project name passed in by the user. There is a mismatch between what is being checked and what is being used as the shell command argument in DiagnosisService. This may cause an illegal project name to pass the check and perform the following steps, resulting in a command injection vulnerability. This issue affects Apache Kylin 4.0.0.

## References
- http://www.openwall.com/lists/oss-security/2022/01/06/1
- https://lists.apache.org/thread/70fkf9w1swt2cqdcz13rwfjvblw1fcpf
