# [M] Disclosure of hosts and related data, linked to decommissioned services in Icinga Web 2

## Summary
Severity: Medium
Advisory: CVE-2022-24714
Aliases: GHSA-qcmg-vr56-x9wf
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-03-08
Source: https://osv.dev/vulnerability/CVE-2022-24714
Type: osv

## Details
Icinga Web 2 is an open source monitoring web interface, framework and command-line interface. Installations of Icinga 2 with the IDO writer enabled are affected. If you use service custom variables in role restrictions, and you regularly decommission service objects, users with said roles may still have access to a collection of content. Note that this only applies if a role has implicitly permitted access to hosts, due to permitted access to at least one of their services. If access to a host is permitted by other means, no sensible information has been disclosed to unauthorized users. This issue has been resolved in versions 2.8.6, 2.9.6 and 2.10 of Icinga Web 2.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/24xxx/CVE-2022-24714.json
- https://github.com/Icinga/icingaweb2/security/advisories/GHSA-qcmg-vr56-x9wf
- https://nvd.nist.gov/vuln/detail/CVE-2022-24714
- https://security.gentoo.org/glsa/202208-05
- https://github.com/Icinga/icingaweb2/commit/6e989d05a1568a6733a3d912001251acc51d9293
