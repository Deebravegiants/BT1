# [C] Ansible fails to properly mark lookup-plugin results as unsafe

## Summary
Severity: Critical
Advisory: GHSA-w578-j992-554x
CVE: CVE-2017-7481
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-09-06
Source: https://github.com/advisories/GHSA-w578-j992-554x
Type: github-advisory

## Affected
- PyPI: `ansible` — affected >=2.3.0.0 <2.3.1.0
- PyPI: `ansible` — affected >=0 <2.1.6.0
- PyPI: `ansible` — affected >=2.2.0.0 <2.2.3.0

## Details
Ansible before versions 2.1.6.0, 2.2.3.0, 2.3.1.0, and 2.4.0.0 fails to properly mark lookup-plugin results as unsafe. If an attacker could control the results of lookup() calls, they could inject Unicode strings to be parsed by the jinja2 templating system, resulting in code execution. By default, the jinja2 templating language is now marked as 'unsafe' and is not evaluated.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-7481
- https://github.com/ansible/ansible/commit/fd30f5328986f9e1da434474481f32bf918a600c
- https://github.com/ansible/ansible/commit/f0e348f5eeb70c1fb3127d90891da43b5c0a9d29
- https://github.com/ansible/ansible/commit/ed56f51f185a1ffd7ea57130d260098686fcc7c2
- https://github.com/ansible/ansible/commit/a1886911fcf4b691130cfc70dfc5daa5e07c46a3
- https://web.archive.org/web/20170801122609/http://www.securityfocus.com/bid/98492
- https://usn.ubuntu.com/4072-1
- https://lists.debian.org/debian-lts-announce/2021/01/msg00023.html
- https://github.com/pypa/advisory-database/tree/main/vulns/ansible/PYSEC-2018-41.yaml
- https://github.com/ansible/ansible
- https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2017-7481
- https://access.redhat.com/errata/RHSA-2017:2524
- https://access.redhat.com/errata/RHSA-2017:1599
- https://access.redhat.com/errata/RHSA-2017:1499
- https://access.redhat.com/errata/RHSA-2017:1476
- https://access.redhat.com/errata/RHSA-2017:1334
- https://access.redhat.com/errata/RHSA-2017:1244
