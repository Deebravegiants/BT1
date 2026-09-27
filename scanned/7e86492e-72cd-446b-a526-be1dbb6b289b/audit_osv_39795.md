# [C] GDAL Bundled zlib (inftree9.c) Pointer Offset Optimization Undefined Behavior Allows Heap Corruption or Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-4738
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:A/S:P/AU:Y/R:U/V:C/RE:L/U:Amber)
Published: 2026-03-24
Source: https://osv.dev/vulnerability/CVE-2026-4738
Type: osv

## Details
Improper Restriction of Operations within the Bounds of a Memory Buffer vulnerability in OSGeo gdal (frmts/zlib/contrib/infback9 modules). This vulnerability is associated with program files inftree9.C‎.

This issue affects gdal: before 3.11.0.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/4xxx/CVE-2026-4738.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-4738
- https://github.com/OSGeo/gdal/pull/12244
- https://github.com/OSGeo/gdal
