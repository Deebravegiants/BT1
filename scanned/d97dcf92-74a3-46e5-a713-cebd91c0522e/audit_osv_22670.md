# [H] Rizin Out-of-bounds Write vulnerability in pyc/marshal.c

## Summary
Severity: High
Advisory: CVE-2022-36040
Aliases: GHSA-h897-rhm9-rpmw
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-06
Source: https://osv.dev/vulnerability/CVE-2022-36040
Type: osv

## Details
Rizin is a UNIX-like reverse engineering framework and command-line toolset. Versions 0.4.0 and prior are vulnerable to an out-of-bounds write when getting data from PYC(python) files. A user opening a malicious PYC file could be affected by this vulnerability, allowing an attacker to execute code on the user's machine. Commit number 68948017423a12786704e54227b8b2f918c2fd27 contains a patch.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36040.json
- https://github.com/rizinorg/rizin/security/advisories/GHSA-h897-rhm9-rpmw
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WQZLMHEI5D7EJASA5UW6XN4ODHLRHK6N/
- https://nvd.nist.gov/vuln/detail/CVE-2022-36040
- https://security.gentoo.org/glsa/202209-06
- https://github.com/rizinorg/rizin/issues/2963
- https://github.com/rizinorg/rizin/commit/68948017423a12786704e54227b8b2f918c2fd27
