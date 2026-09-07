# [C] Remote code execution in net.mingsoft:ms-mcms

## Summary
Severity: Critical
Advisory: GHSA-qwh6-xwj4-9cjg
CVE: CVE-2021-46384
CWE: CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-05
Source: https://github.com/advisories/GHSA-qwh6-xwj4-9cjg
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0 <5.2.6

## Details
net.mingsoft:ms-mcms <=5.2.5 is affected by: RCE. The impact is: execute arbitrary code (remote). The attack vector is: ${"freemarker.template.utility.Execute"?new()("calc")}. ¶¶ MCMS has a pre-auth RCE vulnerability through which allows unauthenticated attacker with network access via http to compromise MCMS. Successful attacks of this vulnerability can result in takeover of MCMS.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-46384
- https://gitee.com/mingSoft/MCMS/issues/I4QZ1O
