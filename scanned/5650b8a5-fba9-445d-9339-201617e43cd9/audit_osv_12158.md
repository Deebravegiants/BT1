# [H] CVE-2018-10642

## Summary
Severity: High
Advisory: CVE-2018-10642
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-05-02
Source: https://osv.dev/vulnerability/CVE-2018-10642
Type: osv

## Details
Command injection vulnerability in Combodo iTop 2.4.1 allows remote authenticated administrators to execute arbitrary commands by changing the platform configuration, because web/env-production/itop-config/config.php contains a function called TestConfig() that calls the vulnerable function eval().

## References
- https://sourceforge.net/p/itop/tickets/1585/
- https://github.com/arbahayoub/POC/blob/master/itop_command_injection_1.txt
