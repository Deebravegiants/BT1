# [M] instack-undercloud vulnerable to symlink attack on tmp files

## Summary
Severity: Medium
Advisory: GHSA-53wm-97p6-582f
CVE: CVE-2017-7549
CWE: CWE-377, CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-53wm-97p6-582f
Type: github-advisory

## Affected
- PyPI: `instack-undercloud` — affected >=0

## Details
A flaw was found in instack-undercloud 7.2.0 as packaged in Red Hat OpenStack Platform Pike, 6.1.0 as packaged in Red Hat OpenStack Platform Oacta, 5.3.0 as packaged in Red Hat OpenStack Newton, where pre-install and security policy scripts used insecure temporary files. A local user could exploit this flaw to conduct a symbolic-link attack, allowing them to overwrite the contents of arbitrary files.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7549
- https://access.redhat.com/errata/RHSA-2017:2557
- https://access.redhat.com/errata/RHSA-2017:2649
- https://access.redhat.com/errata/RHSA-2017:2687
- https://access.redhat.com/errata/RHSA-2017:2693
- https://access.redhat.com/errata/RHSA-2017:2726
- https://access.redhat.com/security/cve/CVE-2017-7549
- https://bugzilla.redhat.com/show_bug.cgi?id=1477403
- https://github.com/pypa/advisory-database/tree/main/vulns/instack/PYSEC-2017-152.yaml
- https://opendev.org/openstack/instack-undercloud
- https://web.archive.org/web/20170907040549/http://www.securityfocus.com/bid/100407
- http://www.securityfocus.com/bid/100407
