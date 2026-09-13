# [H] CVE-2017-16660

## Summary
Severity: High
Advisory: CVE-2017-16660
CVSS: 7.2 (CVSS:3.0/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-11-08
Source: https://osv.dev/vulnerability/CVE-2017-16660
Type: osv

## Details
Cacti 1.1.27 allows remote authenticated administrators to conduct Remote Code Execution attacks by placing the Log Path under the web root, and then making a remote_agent.php request containing PHP code in a Client-ip header.

## References
- https://github.com/Cacti/cacti/issues/1066
