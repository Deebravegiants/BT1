# [H] Nicotine+ DoS on Null Character in Download Request

## Summary
Severity: High
Advisory: GHSA-p4v2-r99v-wjc2
CVE: CVE-2021-45848
CWE: CWE-116
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-16
Source: https://github.com/advisories/GHSA-p4v2-r99v-wjc2
Type: github-advisory

## Affected
- PyPI: `nicotine-plus` — affected >=3.0.3 <3.2.1

## Details
Denial of service (DoS) vulnerability in Nicotine+ starting with version 3.0.3 and prior to version 3.2.1 allows a user with a modified Soulseek client to crash Nicotine+ by sending a file download request with a file path containing a null character.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45848
- https://github.com/nicotine-plus/nicotine-plus/issues/1777
- https://github.com/nicotine-plus/nicotine-plus/commit/0e3e2fac27a518f0a84330f1ddf1193424522045
- https://github.com/nicotine-plus/nicotine-plus
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/HWYV53KERFH2EC4XI2IVVQFTV75E5XM6
- https://security.gentoo.org/glsa/202210-20
