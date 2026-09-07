# [H] XWiki vulnerable to remote code execution with script right through unprotected Velocity scripting API

## Summary
Severity: High
Advisory: GHSA-h259-74h5-4rh9
CVE: CVE-2026-33229
CWE: CWE-862
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-08
Source: https://github.com/advisories/GHSA-h259-74h5-4rh9
Type: github-advisory

## Affected
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=17.0.0-rc-1 <17.4.8
- Maven: `org.xwiki.platform:xwiki-platform-oldcore` — affected >=17.5.0-rc-1 <17.10.1
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=17.0.0-rc-1 <17.4.8
- Maven: `org.xwiki.platform:xwiki-platform-legacy-oldcore` — affected >=17.5.0-rc-1 <17.10.1

## Details
### Impact
An improperly protected scripting API allows any user with script right to bypass the sandboxing of the Velocity scripting API and execute, e.g., arbitrary Python scripts, allowing full access to the XWiki instance and thereby compromising the confidentiality, integrity and availability of the whole instance. Note that script right already constitutes a high level of access that we don't recommend giving to untrusted users.

### Patches
The vulnerability has been patched in XWiki 17.4.8 and 17.10.1 by requiring programming right to access the affected scripting API.

### Workarounds
We're not aware of any workarounds except for being careful whom you grant script right.

### Attribution
We thank Youssef Azefzaf for discovering and reporting this vulnerability.

## References
- https://github.com/xwiki/xwiki-platform/security/advisories/GHSA-h259-74h5-4rh9
- https://nvd.nist.gov/vuln/detail/CVE-2026-33229
- https://github.com/xwiki/xwiki-platform/commit/9fe84da66184c05953df9466cf3a4acd15a46e63
- https://github.com/xwiki/xwiki-platform
- https://jira.xwiki.org/browse/XWIKI-23698
- https://jira.xwiki.org/browse/XWIKI-23702
