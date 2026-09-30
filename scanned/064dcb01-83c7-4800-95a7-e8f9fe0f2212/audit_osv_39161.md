# [C] efw4.X: Path Traversal via Unchecked dst Parameter leads to Remote Code Execution

## Summary
Severity: Critical
Advisory: CVE-2026-44258
Aliases: GHSA-9g5w-qw96-jr3x
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-05-12
Source: https://osv.dev/vulnerability/CVE-2026-44258
Type: osv

## Details
efw4.X is an Enterprise Framework for Web. Prior to 4.08.010, the elfinder_checkRisk function validates target and targets for path traversal and home containment, but does not validate the dst (destination) parameter used by elfinder_paste. An attacker can copy or move files from within the home directory to any arbitrary destination by setting dst to a base64-encoded traversal path. This bypasses the protected=true security control. This vulnerability is fixed in 4.08.010.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/44xxx/CVE-2026-44258.json
- https://github.com/efwGrp/efw4.X/security/advisories/GHSA-9g5w-qw96-jr3x
- https://nvd.nist.gov/vuln/detail/CVE-2026-44258
