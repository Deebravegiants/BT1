# [C] CVE-2017-2800

## Summary
Severity: Critical
Advisory: CVE-2017-2800
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-24
Source: https://osv.dev/vulnerability/CVE-2017-2800
Type: osv

## Details
A specially crafted x509 certificate can cause a single out of bounds byte overwrite in wolfSSL through 3.10.2 resulting in potential certificate validation vulnerabilities, denial of service and possible remote code execution. In order to trigger this vulnerability, the attacker needs to supply a malicious x509 certificate to either a server or a client application using this library.

## References
- https://talosintelligence.com/vulnerability_reports/TALOS-2017-0293
- https://www.exploit-db.com/exploits/41984/
