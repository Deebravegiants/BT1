# [M] CVE-2018-8949

## Summary
Severity: Medium
Advisory: CVE-2018-8949
CVSS: 4.3 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N)
Published: 2018-03-23
Source: https://osv.dev/vulnerability/CVE-2018-8949
Type: osv

## Details
An issue was discovered in app/Model/Attribute.php in MISP before 2.4.89. There is a critical API integrity bug, potentially allowing users to delete attributes of other events. A crafted edit for an event (without attribute UUIDs but attribute IDs set) could overwrite an existing attribute.

## References
- https://github.com/MISP/MISP/commit/37720c38d6c617439df0a13e9396fcb26345dadd
