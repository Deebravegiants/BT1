# [H] Privilege escalation on xrdp

## Summary
Severity: High
Advisory: CVE-2022-23613
Aliases: GHSA-8h98-h426-xf32
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-07
Source: https://osv.dev/vulnerability/CVE-2022-23613
Type: osv

## Details
xrdp is an open source remote desktop protocol (RDP) server. In affected versions an integer underflow leading to a heap overflow in the sesman server allows any unauthenticated attacker which is able to locally access a sesman server to execute code as root. This vulnerability has been patched in version 0.9.18.1 and above. Users are advised to upgrade. There are no known workarounds.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23613.json
- https://github.com/neutrinolabs/xrdp/security/advisories/GHSA-8h98-h426-xf32
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/K5ONRGARKHGFU2CIEQ7E6M6VJZEM5XWW/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/U3XGFJNQMNXHBD3J7CBM4YURYEDXROWZ/
- https://nvd.nist.gov/vuln/detail/CVE-2022-23613
- https://github.com/neutrinolabs/xrdp/commit/4def30ab8ea445cdc06832a44c3ec40a506a0ffa
