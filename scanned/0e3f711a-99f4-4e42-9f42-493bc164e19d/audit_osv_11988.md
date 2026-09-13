# [H] CVE-2018-1000542

## Summary
Severity: High
Advisory: CVE-2018-1000542
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2018-06-26
Source: https://osv.dev/vulnerability/CVE-2018-1000542
Type: osv

## Details
netbeans-mmd-plugin version <= 1.4.3 contains a XML External Entity (XXE) vulnerability in MMD file import that can result in Possible information disclosure, server-side request forgery, or remote code execution. This attack appear to be exploitable via Specially crafted MMD file.

## References
- https://0dd.zone/2018/06/02/Netbeans-MMD-Plugin-XXE/
- https://github.com/raydac/netbeans-mmd-plugin/issues/45
