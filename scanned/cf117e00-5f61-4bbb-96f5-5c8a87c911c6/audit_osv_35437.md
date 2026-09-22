# [C] CVE-2025-8343

## Summary
Severity: Critical
Advisory: CVE-2025-8343
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-07-31
Source: https://osv.dev/vulnerability/CVE-2025-8343
Type: osv

## Details
A vulnerability was found in openviglet shio up to 0.3.8. It has been rated as critical. This issue affects the function shStaticFilePreUpload of the file shio-app/src/main/java/com/viglet/shio/api/staticfile/ShStaticFileAPI.java. The manipulation of the argument fileName leads to path traversal. The attack may be initiated remotely. The exploit has been disclosed to the public and may be used.

## References
- https://vuldb.com/?id.318293
- https://vuldb.com/?submit.617679
- https://github.com/openviglet/shio/issues/1028
- https://github.com/openviglet/shio/issues/1028#issue-3239418750
- https://vuldb.com/?ctiid.318293
