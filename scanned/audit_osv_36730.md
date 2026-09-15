# [M] Group-Office is vulnerable to SSRF and File Read in WOPI service discovery

## Summary
Severity: Medium
Advisory: CVE-2026-25511
Aliases: GHSA-r9v4-jm2r-r9pm
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N)
Published: 2026-02-04
Source: https://osv.dev/vulnerability/CVE-2026-25511
Type: osv

## Details
Group-Office is an enterprise customer relationship management and groupware tool. Prior to versions 6.8.150, 25.0.82, and 26.0.5, an authenticated user within the System Administrator group can trigger a full SSRF via the WOPI service discovery URL, including access to internal hosts/ports. The SSRF response body can be exfiltrated via the built‑in debug system, turning it into a visible SSRF. This also allows full server-side file read. This issue has been patched in versions 6.8.150, 25.0.82, and 26.0.5.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25511.json
- https://github.com/Intermesh/groupoffice/security/advisories/GHSA-r9v4-jm2r-r9pm
- https://nvd.nist.gov/vuln/detail/CVE-2026-25511
- https://github.com/Intermesh/groupoffice/commit/5ac199dce758e1ce0d1cdb6905df5da3c2af42b3
