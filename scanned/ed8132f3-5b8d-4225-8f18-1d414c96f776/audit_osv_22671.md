# [H] Rizin Out-of-bounds Write vulnerability in Mach-O binary plugin

## Summary
Severity: High
Advisory: CVE-2022-36041
Aliases: GHSA-2c7m-2f37-mr5m
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-06
Source: https://osv.dev/vulnerability/CVE-2022-36041
Type: osv

## Details
Rizin is a UNIX-like reverse engineering framework and command-line toolset. Versions 0.4.0 and prior are vulnerable to an out-of-bounds write when parsing Mach-O files. A user opening a malicious Mach-O file could be affected by this vulnerability, allowing an attacker to execute code on the user's machine. Commit number 7323e64d68ecccfb0ed3ee480f704384c38676b2 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36041.json
- https://github.com/rizinorg/rizin/security/advisories/GHSA-2c7m-2f37-mr5m
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WQZLMHEI5D7EJASA5UW6XN4ODHLRHK6N/
- https://nvd.nist.gov/vuln/detail/CVE-2022-36041
- https://security.gentoo.org/glsa/202209-06
- https://github.com/rizinorg/rizin/issues/2956
- https://github.com/rizinorg/rizin/commit/7323e64d68ecccfb0ed3ee480f704384c38676b2
