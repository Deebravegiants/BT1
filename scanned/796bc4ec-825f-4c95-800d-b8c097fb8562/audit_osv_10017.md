# [M] CVE-2017-12779

## Summary
Severity: Medium
Advisory: CVE-2017-12779
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-11-10
Source: https://osv.dev/vulnerability/CVE-2017-12779
Type: osv

## Details
The Node_GetData function in corec/corec/node/node.c in mkvalidator 0.5.1 allows remote attackers to cause a denial of service (Null pointer dereference and application crash) via a crafted mkv file.

## References
- http://packetstormsecurity.com/files/144902/mkvalidator-0.5.1-Denial-Of-Service.html
- http://seclists.org/fulldisclosure/2017/Nov/19
- https://github.com/Matroska-Org/foundation-source/issues/24
