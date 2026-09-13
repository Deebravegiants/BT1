# [H] Exposure of Resource to Wrong Sphere in salt

## Summary
Severity: High
Advisory: GHSA-pf7h-h2wq-m7pg
CVE: CVE-2021-21996
CWE: CWE-668
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-11-21
Source: https://github.com/advisories/GHSA-pf7h-h2wq-m7pg
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <3003.3

## Details
An issue was discovered in SaltStack Salt before 3003.3. A user who has control of the source, and source_hash URLs can gain full file system access as root on a salt minion.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-21996
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2021-318.yaml
- https://github.com/saltstack/salt
- https://lists.debian.org/debian-lts-announce/2021/11/msg00017.html
- https://lists.debian.org/debian-lts-announce/2021/11/msg00019.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/6BUWUF5VTENNP2ZYZBVFKPSUHLKLUBD5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ACVT7M4YLZRLWWQ6SGRK3C6TOF4FXOXT
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/MBAHHSGZLEJRCG4DX6J4RBWJAAWH55RQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/6BUWUF5VTENNP2ZYZBVFKPSUHLKLUBD5
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ACVT7M4YLZRLWWQ6SGRK3C6TOF4FXOXT
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/MBAHHSGZLEJRCG4DX6J4RBWJAAWH55RQ
- https://saltproject.io/security_announcements/salt-security-advisory-2021-sep-02
- https://security.gentoo.org/glsa/202310-22
- https://www.debian.org/security/2021/dsa-5011
