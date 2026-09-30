# [H] koji hub allows arbitrary upload destinations

## Summary
Severity: High
Advisory: GHSA-7498-c9fm-g64p
CVE: CVE-2019-17109
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-7498-c9fm-g64p
Type: github-advisory

## Affected
- PyPI: `koji` — affected >=1.14.0 <1.14.3
- PyPI: `koji` — affected >=1.15.0 <1.15.3
- PyPI: `koji` — affected >=1.16.0 <1.16.3
- PyPI: `koji` — affected >=1.17.0 <1.17.1
- PyPI: `koji` — affected >=1.18.0 <1.18.1

## Details
The way that the hub code validates upload paths allows for an attacker to choose an arbitrary destination for the uploaded file.
Uploading still requires login. However, an attacker with credentials could damage the integrity of the Koji system.

### Workaround
There is no known workaround. All Koji admins are encouraged to update to a fixed version as soon as possible.

### Fix
Koji versions 1.14.3, 1.15.3, 1.16.3, 1.17.1, and 1.18.1 all include patches to solve this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-17109
- https://github.com/koji-project/koji/commit/91d6f0b607c7f5af666dfb56931f1db4e38c28a5
- https://docs.pagure.org/koji/CVE-2019-17109
- https://github.com/koji-project/koji
- https://github.com/koji-project/koji/blob/d0507c4d2d2269daa984db642e3bd957dff18948/docs/source/CVEs/CVE-2019-17109.rst
- https://github.com/pypa/advisory-database/tree/main/vulns/koji/PYSEC-2019-183.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/4BGUXMZIAQFFNNQ7PEFDAYQCXXKJR76U
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/7PSCCFHLNVFLDPC7DB4UJGXD6ZWBSY57
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/DEQYYGWLJBQQVTAC7E7XSDGVF27NPMPB
- https://pagure.io/koji/commits/master
- https://pagure.io/koji/issue/1634
- https://pagure.io/koji/pull-request/1686
- http://www.openwall.com/lists/oss-security/2019/10/09/5
