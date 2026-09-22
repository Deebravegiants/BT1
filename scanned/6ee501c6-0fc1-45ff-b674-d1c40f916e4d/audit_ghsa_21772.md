# [H] Command Injection in Cobbler

## Summary
Severity: High
Advisory: GHSA-6cm4-gm85-972c
CVE: CVE-2021-45082
CWE: CWE-77
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-20
Source: https://github.com/advisories/GHSA-6cm4-gm85-972c
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=0 <3.3.1

## Details
An issue was discovered in Cobbler through 3.3.0. In the templar.py file, the function check_for_invalid_imports can allow Cheetah code to import Python modules via the "#from MODULE import" substring. (Only lines beginning with #import are blocked.)

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-45082
- https://github.com/cobbler/cobbler/pull/2945
- https://bugzilla.suse.com/show_bug.cgi?id=1193678
- https://github.com/cobbler/cobbler
- https://github.com/cobbler/cobbler/releases
- https://github.com/cobbler/cobbler/releases/tag/v3.3.1
- https://github.com/pypa/advisory-database/tree/main/vulns/cobbler/PYSEC-2022-37.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/TEJN7CPW6YCHBFQPFZKGA6AVA6T5NPIW
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z5CSXQE7Q4TVDQJKFYBO4XDH3BZ7BLAR
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/ZCXMOUW4DH4DYWIJN44SMSU6R3CZDZBE
