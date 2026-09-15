# [H] Incorrect Default Permissions in Cobbler

## Summary
Severity: High
Advisory: GHSA-5946-mpw5-pqxx
CVE: CVE-2021-45083
CWE: CWE-276
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-02-21
Source: https://github.com/advisories/GHSA-5946-mpw5-pqxx
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=0 <3.3.1

## Details
An issue was discovered in Cobbler before 3.3.1. Files in /etc/cobbler are world readable. Two of those files contain some sensitive information that can be exposed to a local user who has non-privileged access to the server. The users.digest file contains the sha2-512 digest of users in a Cobbler local installation. In the case of an easy-to-guess password, it's trivial to obtain the plaintext string. The settings.yaml file contains secrets such as the hashed default password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45083
- https://github.com/cobbler/cobbler/pull/2945
- https://github.com/cobbler/cobbler/commit/10b2112db83fedfc391e900edfedc2b4e507d3f7
- https://bugzilla.suse.com/show_bug.cgi?id=1193671
- https://github.com/advisories/GHSA-5946-mpw5-pqxx
- https://github.com/cobbler/cobbler
- https://github.com/cobbler/cobbler/releases
- https://github.com/cobbler/cobbler/releases/tag/v3.3.1
- https://github.com/pypa/advisory-database/tree/main/vulns/cobbler/PYSEC-2022-38.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TEJN7CPW6YCHBFQPFZKGA6AVA6T5NPIW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z5CSXQE7Q4TVDQJKFYBO4XDH3BZ7BLAR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZCXMOUW4DH4DYWIJN44SMSU6R3CZDZBE
- https://www.openwall.com/lists/oss-security/2022/02/18/3
