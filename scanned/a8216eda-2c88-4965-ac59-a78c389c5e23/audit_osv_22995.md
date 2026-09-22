# [M] Privilege Escalation Vulnerability by wrong chmod param

## Summary
Severity: Medium
Advisory: CVE-2022-41950
Aliases: GHSA-2g28-xrw6-fq5f
CVSS: 6.4 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-22
Source: https://osv.dev/vulnerability/CVE-2022-41950
Type: osv

## Details
super-xray is the GUI alternative for vulnerability scanning tool xray. In 0.2-beta, a privilege escalation vulnerability was discovered. This caused inaccurate default xray permissions. Note: this vulnerability only affects Linux and Mac OS systems. Users should upgrade to super-xray 0.3-beta.

## References
- https://github.com/4ra1n/super-xray/releases/tag/0.3-beta
- https://github.com/4ra1n/super-xray/security/advisories/GHSA-2g28-xrw6-fq5f
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41950.json
- https://nvd.nist.gov/vuln/detail/CVE-2022-41950
