# [M] CVE-2017-12803

## Summary
Severity: Medium
Advisory: CVE-2017-12803
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-10
Source: https://osv.dev/vulnerability/CVE-2017-12803
Type: osv

## Details
The Node_ValidatePtr function in corec/corec/node/node.c in mkclean 0.8.9 allows remote attackers to cause a denial of service (assert fault) via a crafted mkv file.

## References
- http://packetstormsecurity.com/files/144902/mkvalidator-0.5.1-Denial-Of-Service.html
- http://seclists.org/fulldisclosure/2017/Nov/19
- https://github.com/Matroska-Org/foundation-source/issues/24
