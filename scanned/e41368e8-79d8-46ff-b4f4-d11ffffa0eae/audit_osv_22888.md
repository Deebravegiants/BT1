# [H] CVE-2022-40284

## Summary
Severity: High
Advisory: CVE-2022-40284
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-06
Source: https://osv.dev/vulnerability/CVE-2022-40284
Type: osv

## Details
A buffer overflow was discovered in NTFS-3G before 2022.10.3. Crafted metadata in an NTFS image can cause code execution. A local attacker can exploit this if the ntfs-3g binary is setuid root. A physically proximate attacker can exploit this if NTFS-3G software is configured to execute upon attachment of an external storage device.

## References
- http://www.openwall.com/lists/oss-security/2022/10/31/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/40xxx/CVE-2022-40284.json
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2BOQ7YLFT43KLXEN3EB6CS4DP635RJWP/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/IA2D4PYOR7ABI7BWBMMMYKY2OPHTV2NI/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/UGDKGXA4R2ZVUQ3CT4D4YGTFMNZQA7HW/
- https://nvd.nist.gov/vuln/detail/CVE-2022-40284
- https://security.gentoo.org/glsa/202301-01
- https://github.com/tuxera/ntfs-3g/releases
- https://lists.debian.org/debian-lts-announce/2022/11/msg00029.html
