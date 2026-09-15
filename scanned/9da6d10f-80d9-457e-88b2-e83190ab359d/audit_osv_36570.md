# [H] iccDEV has Heap Buffer Overflow in icCurvesFromXml()

## Summary
Severity: High
Advisory: CVE-2026-24412
Aliases: GHSA-6rf4-63j2-cfrf
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2026-01-24
Source: https://osv.dev/vulnerability/CVE-2026-24412
Type: osv

## Details
iccDEV provides libraries and tools for interacting with, manipulating, and applying ICC color management profiles. Versions 2.3.1.1 and below have aHeap Buffer Overflow vulnerability in the CIccTagXmlSegmentedCurve::ToXml() function. This occurs when user-controllable input is unsafely incorporated into ICC profile data or other structured binary blobs. Successful exploitation may allow an attacker to perform DoS, manipulate data, bypass application logic and Code Execution. This issue has been fixed in version 2.3.1.2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/24xxx/CVE-2026-24412.json
- https://github.com/InternationalColorConsortium/iccDEV/security/advisories/GHSA-6rf4-63j2-cfrf
- https://nvd.nist.gov/vuln/detail/CVE-2026-24412
- https://github.com/InternationalColorConsortium/iccDEV/issues/518
- https://github.com/InternationalColorConsortium/iccDEV/commit/2be3b125933a57fe8b6624e9dfd69d8e5360bf70
