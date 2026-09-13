# [H] CVE-2019-15588

## Summary
Severity: High
Advisory: CVE-2019-15588
CVSS: 7.2 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-01
Source: https://osv.dev/vulnerability/CVE-2019-15588
Type: osv

## Details
There is an OS Command Injection in Nexus Repository Manager <= 2.14.14 (bypass CVE-2019-5475) that could allow an attacker a Remote Code Execution (RCE). All instances using CommandLineExecutor.java with user-supplied data is vulnerable, such as the Yum Configuration Capability.

## References
- https://support.sonatype.com/hc/en-us/articles/360033490774-CVE-2019-5475-Nexus-Repository-Manager-2-OS-Command-Injection-2019-08-09
- https://hackerone.com/reports/688270
