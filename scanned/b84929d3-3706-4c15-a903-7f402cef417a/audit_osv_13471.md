# [M] CVE-2018-1999018

## Summary
Severity: Medium
Advisory: CVE-2018-1999018
CVSS: 6.6 (CVSS:3.0/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-23
Source: https://osv.dev/vulnerability/CVE-2018-1999018
Type: osv

## Details
Pydio version 8.2.1 and prior contains an Unvalidated user input leading to Remote Code Execution (RCE) vulnerability in plugins/action.antivirus/AntivirusScanner.php: Line 124, scanNow($nodeObject) that can result in An attacker gaining admin access and can then execute arbitrary commands on the underlying OS. This attack appear to be exploitable via The attacker edits the Antivirus Command in the antivirus plugin, and executes the payload by uploading any file within Pydio.

## References
- https://www.mike-gualtieri.com/files/Pydio-8-VulnerabilityDisclosure-Jul18.txt
