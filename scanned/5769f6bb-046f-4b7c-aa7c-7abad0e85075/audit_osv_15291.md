# [H] CVE-2019-15033

## Summary
Severity: High
Advisory: CVE-2019-15033
CVSS: 7.7 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N)
Published: 2019-09-19
Source: https://osv.dev/vulnerability/CVE-2019-15033
Type: osv

## Details
Pydio 6.0.8 allows Authenticated SSRF during a Remote Link Feature download. An attacker can specify an intranet address in the file parameter to index.php, when sending a file to a remote server, as demonstrated by the file=http%3A%2F%2F192.168.1.2 substring.

## References
- https://pydio.com
- https://sourceforge.net/projects/ajaxplorer/files/pydio/stable-channel/
- https://heitorgouvea.me/2019/09/17/CVE-2019-15033
