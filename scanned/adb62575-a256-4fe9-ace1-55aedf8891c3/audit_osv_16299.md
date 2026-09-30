# [C] CVE-2019-5029

## Summary
Severity: Critical
Advisory: CVE-2019-5029
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-11-13
Source: https://osv.dev/vulnerability/CVE-2019-5029
Type: osv

## Details
An exploitable command injection vulnerability exists in the Config editor of the Exhibitor Web UI versions 1.0.9 to 1.7.1. Arbitrary shell commands surrounded by backticks or $() can be inserted into the editor and will be executed by the Exhibitor process when it launches ZooKeeper. An attacker can execute any command as the user running the Exhibitor process.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2019-0790
