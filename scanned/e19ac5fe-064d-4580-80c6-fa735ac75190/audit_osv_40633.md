# [M] Cerebrate before v1.37 allows mass assignment of record identifiers during object creation

## Summary
Severity: Medium
Advisory: CVE-2026-53901
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:L/SA:N/U:Amber)
Published: 2026-06-11
Source: https://osv.dev/vulnerability/CVE-2026-53901
Type: osv

## Details
Cerebrate before version 1.37 contains a mass-assignment vulnerability in the generic CRUD add path. The add() handler attempted to remove an attacker-supplied id from $params before normalizing the request through __massageInput(). Because the normalized $input could still contain an id field, a user able to reach an affected add endpoint could supply an identifier that should have been server-controlled.


Successful exploitation could allow creation of objects with attacker-chosen identifiers, potentially causing unauthorized data manipulation, object spoofing, inconsistent references, or disruption through identifier collisions, depending on the affected model and endpoint permissions. The issue was fixed in v1.37 by removing id from the normalized input before entity patching.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/53xxx/CVE-2026-53901.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-53901
- https://github.com/cerebrate-project/cerebrate/commit/aff1ca707c8f926d00cda3deb39ff9bf59cdf18e
