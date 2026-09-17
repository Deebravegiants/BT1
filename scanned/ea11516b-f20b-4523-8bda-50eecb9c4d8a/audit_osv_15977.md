# [C] CVE-2019-20914

## Summary
Severity: Critical
Advisory: CVE-2019-20914
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-07-16
Source: https://osv.dev/vulnerability/CVE-2019-20914
Type: osv

## Details
An issue was discovered in GNU LibreDWG through 0.9.3. There is a NULL pointer dereference in the function dwg_encode_common_entity_handle_data in common_entity_handle_data.spec.

## References
- https://github.com/LibreDWG/libredwg/commit/3b837bb72d6b9ab4d563faa211f90efc257e3c96
- https://github.com/LibreDWG/libredwg/issues/178
