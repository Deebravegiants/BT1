# [C] bullet3 VHACD utility: stack-based buffer overflow in OFF parser (LoadOFF)

## Summary
Severity: Critical
Advisory: CVE-2025-8854
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-08-11
Source: https://osv.dev/vulnerability/CVE-2025-8854
Type: osv

## Details
Stack-based buffer overflow in LoadOFF in bulletphysics bullet3 before 3.26 on all platforms allows remote attackers to execute arbitrary code via a crafted OFF file with an overlong initial token processed by the VHACD test utility or invoked indirectly through PyBullet's vhacd function.

## References
- https://github.com/bulletphysics/bullet3/blob/master/Extras/VHACD/test/src/main_vhacd.cpp#L472
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/8xxx/CVE-2025-8854.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-8854
- https://github.com/bulletphysics/bullet3/issues/4732
