# [H] DOS attack in Pillow when processing specially crafted image files

## Summary
Severity: High
Advisory: GHSA-j7mj-748x-7p78
CVE: CVE-2019-16865
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2019-10-22
Source: https://github.com/advisories/GHSA-j7mj-748x-7p78
Type: github-advisory

## Affected
- PyPI: `pillow` — affected >=0 <6.2.0

## Details
An issue was discovered in Pillow before 6.2.0. When reading specially crafted invalid image files, the library can either allocate very large amounts of memory or take an extremely long period of time to process the image.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-16865
- https://github.com/python-pillow/Pillow/issues/4123
- https://github.com/python-pillow/Pillow/commit/ab52630d0644e42a75eb88b78b9a9d7438a6fbeb
- https://www.debian.org/security/2020/dsa-4631
- https://usn.ubuntu.com/4272-1
- https://ubuntu.com/security/notices/USN-4272-1
- https://pillow.readthedocs.io/en/latest/releasenotes/6.2.0.html
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/LYDXD7EE4YAEVSTNIFZKNVPRVJX5ZOG3
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/EMJBUZQGQ2Q7HXYCQVRLU7OXNC7CAWWU
- https://github.com/python-pillow/Pillow
- https://github.com/pypa/advisory-database/tree/main/vulns/pillow/PYSEC-2019-110.yaml
- https://github.com/advisories/GHSA-j7mj-748x-7p78
- https://access.redhat.com/errata/RHSA-2020:0694
- https://access.redhat.com/errata/RHSA-2020:0683
- https://access.redhat.com/errata/RHSA-2020:0681
- https://access.redhat.com/errata/RHSA-2020:0580
- https://access.redhat.com/errata/RHSA-2020:0578
- https://access.redhat.com/errata/RHSA-2020:0566
