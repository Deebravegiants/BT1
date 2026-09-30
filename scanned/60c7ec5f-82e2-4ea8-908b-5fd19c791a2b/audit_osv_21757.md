# [M] CVE-2021-46225

## Summary
Severity: Medium
Advisory: CVE-2021-46225
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2022-01-12
Source: https://osv.dev/vulnerability/CVE-2021-46225
Type: osv

## Details
A buffer overflow in the GmfOpenMesh() function of libMeshb v7.61 allows attackers to cause a Denial of Service (DoS) via a crafted MESH file.

## References
- https://github.com/LoicMarechal/libMeshb/issues/21
- https://github.com/LoicMarechal/libMeshb/commit/8cd68c54e0647c0030ae4506a225ad4a2655c316
