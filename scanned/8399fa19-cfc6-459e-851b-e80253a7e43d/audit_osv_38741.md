# [M] Vvveb < 1.0.8.3 Uncontrolled Recursion Denial of Service

## Summary
Severity: Medium
Advisory: CVE-2026-41935
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:N/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-14
Source: https://osv.dev/vulnerability/CVE-2026-41935
Type: osv

## Details
Vvveb before 1.0.8.3 contains an uncontrolled recursion vulnerability in the admin controller dispatch cycle where Base::init() repeatedly invokes permission() on error handlers, causing infinite recursion until PHP memory limits are exhausted. Attackers can send sustained requests to forbidden admin URLs from a low-privilege account to exhaust PHP memory on all workers and cause denial of service to legitimate traffic.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41935.json
- https://github.com/givanz/Vvveb/releases/tag/1.0.8.3
- https://nvd.nist.gov/vuln/detail/CVE-2026-41935
- https://www.vulncheck.com/advisories/vvveb-uncontrolled-recursion-denial-of-service
- https://github.com/givanz/Vvveb/commit/c766e84b479dcf1bd1f25a44e4b9c9fa450769c8
- https://github.com/givanz/Vvveb
