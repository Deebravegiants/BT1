# [C] Improper Restriction of Operations within the Bounds of a Memory Buffer vulnerability in OSGeo gdal...

## Summary
Severity: Critical
Advisory: JLSEC-2026-288
Ecosystem: Julia
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H/E:A/CR:X/IR:X/AR:X/MAV:X/MAC:X/MAT:X/MPR:X/MUI:X/MVC:X/MVI:X/MVA:X/MSC:X/MSI:X/MSA:X/S:P/AU:Y/R:U/V:C/RE:L/U:Amber)
Published: 2026-04-28
Source: https://osv.dev/vulnerability/JLSEC-2026-288
Type: osv

## Affected
- Julia: `GDAL_jll` — affected >=0 <303.1100.0+0

## Details
Improper Restriction of Operations within the Bounds of a Memory Buffer vulnerability in OSGeo gdal (frmts/zlib/contrib/infback9 modules). This vulnerability is associated with program files inftree9.C‎.

This issue affects gdal: before 3.11.0.

## References
- https://github.com/OSGeo/gdal/pull/12244
- https://github.com/advisories/GHSA-hp6p-5qh5-w9fj
- https://nvd.nist.gov/vuln/detail/CVE-2026-4738
