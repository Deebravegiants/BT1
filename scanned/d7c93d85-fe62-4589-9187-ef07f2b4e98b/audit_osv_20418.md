# [M] CVE-2021-33491

## Summary
Severity: Medium
Advisory: CVE-2021-33491
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N)
Published: 2021-11-22
Source: https://osv.dev/vulnerability/CVE-2021-33491
Type: osv

## Details
OX App Suite through 7.10.5 allows Directory Traversal via ../ in an OOXML or ODF ZIP archive, because of the mishandling of relative paths in mail addresses in conjunction with auto-configuration DNS records.

## References
- https://open-xchange.com
- http://packetstormsecurity.com/files/165028/OX-App-Suite-Ox-Documents-7.10.x-XSS-Code-Injection-Traversal.html
- https://seclists.org/fulldisclosure/2021/Nov/42
