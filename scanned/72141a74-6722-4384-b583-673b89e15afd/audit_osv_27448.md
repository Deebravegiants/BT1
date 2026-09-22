# [H] Arbitrary file write on Decoding

## Summary
Severity: High
Advisory: CVE-2024-21633
Aliases: GHSA-2hqv-2xv4-5h5w
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2024-01-03
Source: https://osv.dev/vulnerability/CVE-2024-21633
Type: osv

## Details
Apktool is a tool for reverse engineering Android APK files. In versions 2.9.1 and prior, Apktool infers resource files' output path according to their resource names which can be manipulated by attacker to place files at desired location on the system Apktool runs on. Affected environments are those in which an attacker may write/overwrite any file that user has write access, and either user name is known or cwd is under user folder. Commit d348c43b24a9de350ff6e5bd610545a10c1fc712 contains a patch for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/21xxx/CVE-2024-21633.json
- https://github.com/iBotPeaches/Apktool/security/advisories/GHSA-2hqv-2xv4-5h5w
- https://nvd.nist.gov/vuln/detail/CVE-2024-21633
- https://github.com/iBotPeaches/Apktool/commit/d348c43b24a9de350ff6e5bd610545a10c1fc712
