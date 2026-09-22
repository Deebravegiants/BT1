# [H] Bypass of safe.directory protections in Git

## Summary
Severity: High
Advisory: CVE-2022-29187
Aliases: GHSA-j342-m5hw-rr3v
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-12
Source: https://osv.dev/vulnerability/CVE-2022-29187
Type: osv

## Details
Git is a distributed revision control system. Git prior to versions 2.37.1, 2.36.2, 2.35.4, 2.34.4, 2.33.4, 2.32.3, 2.31.4, and 2.30.5, is vulnerable to privilege escalation in all platforms. An unsuspecting user could still be affected by the issue reported in CVE-2022-24765, for example when navigating as root into a shared tmp directory that is owned by them, but where an attacker could create a git repository. Versions 2.37.1, 2.36.2, 2.35.4, 2.34.4, 2.33.4, 2.32.3, 2.31.4, and 2.30.5 contain a patch for this issue. The simplest way to avoid being affected by the exploit described in the example is to avoid running git as root (or an Administrator in Windows), and if needed to reduce its use to a minimum. While a generic workaround is not possible, a system could be hardened from the exploit described in the example by removing any such repository if it exists already and creating one as root to block any future attacks.

## References
- https://lore.kernel.org/git/xmqqv8s2fefi.fsf%40gitster.g/T/#u
- https://support.apple.com/kb/HT213496
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/29xxx/CVE-2022-29187.json
- https://github.com/git/git/security/advisories/GHSA-j342-m5hw-rr3v
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DDI325LOO2XBDDKLINOAQJEG6MHAURZE/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/DIKWISWUDFT2FAITYIA6372BVLH3OOOC/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/HVOLER2PIGMHPQMDGG4RDE2KZB74QLA2/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/TRZG5CDUQ27OWTPC5MQOR4UASNXHWEZS/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UDZRZAL7QULOB6V7MKT66MOMWJLBJPX4/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/YROCMBWYFKRSS64PO6FUNM6L7LKBUKVW/
- https://nvd.nist.gov/vuln/detail/CVE-2022-29187
- https://security.gentoo.org/glsa/202312-15
- https://security.gentoo.org/glsa/202401-17
- http://seclists.org/fulldisclosure/2022/Nov/1
- http://www.openwall.com/lists/oss-security/2022/07/14/1
- https://github.blog/2022-04-12-git-security-vulnerability-announced
- https://lists.debian.org/debian-lts-announce/2022/12/msg00025.html
