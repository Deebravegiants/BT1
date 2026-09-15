# [H] Out-of-bounds write when parsing DEX files in Rizin

## Summary
Severity: High
Advisory: CVE-2022-36039
Aliases: GHSA-pr85-hv85-45pg
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2022-09-06
Source: https://osv.dev/vulnerability/CVE-2022-36039
Type: osv

## Details
Rizin is a UNIX-like reverse engineering framework and command-line toolset. Versions 0.4.0 and prior are vulnerable to out-of-bounds write when parsing DEX files. A user opening a malicious DEX file could be affected by this vulnerability, allowing an attacker to execute code on the user's machine. A patch is available on the `dev` branch of the repository.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/36xxx/CVE-2022-36039.json
- https://github.com/rizinorg/rizin/security/advisories/GHSA-pr85-hv85-45pg
- https://nvd.nist.gov/vuln/detail/CVE-2022-36039
- https://security.gentoo.org/glsa/202209-06
- https://github.com/rizinorg/rizin/issues/2969
- https://github.com/rizinorg/rizin/commit/1524f85211445e41506f98180f8f69f7bf115406
