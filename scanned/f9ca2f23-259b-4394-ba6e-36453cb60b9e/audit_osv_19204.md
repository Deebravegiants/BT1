# [H] CVE-2020-8654

## Summary
Severity: High
Advisory: CVE-2020-8654
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-02-07
Source: https://osv.dev/vulnerability/CVE-2020-8654
Type: osv

## Details
An issue was discovered in EyesOfNetwork 5.3. An authenticated web user with sufficient privileges could abuse the AutoDiscovery module to run arbitrary OS commands via the /module/module_frame/index.php autodiscovery.php target field.

## References
- https://github.com/EyesOfNetworkCommunity/eonweb/issues/50
- http://packetstormsecurity.com/files/156266/EyesOfNetwork-5.3-Remote-Code-Execution.html
- http://packetstormsecurity.com/files/156605/EyesOfNetwork-AutoDiscovery-Target-Command-Execution.html
