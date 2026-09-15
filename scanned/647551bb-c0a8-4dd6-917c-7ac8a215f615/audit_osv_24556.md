# [H] CVE-2023-22809

## Summary
Severity: High
Advisory: CVE-2023-22809
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-18
Source: https://osv.dev/vulnerability/CVE-2023-22809
Type: osv

## Details
In Sudo before 1.9.12p2, the sudoedit (aka -e) feature mishandles extra arguments passed in the user-provided environment variables (SUDO_EDITOR, VISUAL, and EDITOR), allowing a local attacker to append arbitrary entries to the list of files to process. This can lead to privilege escalation. Affected versions are 1.8.0 through 1.9.12.p1. The problem exists because a user-specified editor may contain a "--" argument that defeats a protection mechanism, e.g., an EDITOR='vim -- /path/to/extra/file' value.

## References
- http://packetstormsecurity.com/files/171644/sudo-1.9.12p1-Privilege-Escalation.html
- http://packetstormsecurity.com/files/172509/Sudoedit-Extra-Arguments-Privilege-Escalation.html
- http://packetstormsecurity.com/files/174234/Cisco-ThousandEyes-Enterprise-Agent-Virtual-Appliance-Arbitrary-File-Modification.html
- https://support.apple.com/kb/HT213758
- https://www.synacktiv.com/sites/default/files/2023-01/sudo-CVE-2023-22809.pdf
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/22xxx/CVE-2023-22809.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2QDGFCGAV5QRJCE6IXRXIS4XJHS57DDH/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/G4YNBTTKTRT2ME3NTSXAPTOKYUE47XHZ/
- https://nvd.nist.gov/vuln/detail/CVE-2023-22809
- https://security.gentoo.org/glsa/202305-12
- https://security.netapp.com/advisory/ntap-20230127-0015/
- https://www.debian.org/security/2023/dsa-5321
- https://www.sudo.ws/security/advisories/sudoedit_any/
- http://seclists.org/fulldisclosure/2023/Aug/21
- http://www.openwall.com/lists/oss-security/2023/01/19/1
- https://lists.debian.org/debian-lts-announce/2023/01/msg00012.html
