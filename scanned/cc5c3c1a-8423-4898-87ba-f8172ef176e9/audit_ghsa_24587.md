# [H] Cobbler is vulnerable to code injection 

## Summary
Severity: High
Advisory: GHSA-jhm7-38xj-pvm8
CVE: CVE-2010-2235
CWE: CWE-94
Ecosystem: PyPI
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-jhm7-38xj-pvm8
Type: github-advisory

## Affected
- PyPI: `cobbler` — affected >=0 <2.0.7

## Details
template_api.py in Cobbler before 2.0.7, as used in Red Hat Network Satellite Server and other products, does not disable the ability of the Cheetah template engine to execute Python statements contained in templates, which allows remote authenticated administrators to execute arbitrary code via a crafted kickstart template file, a different vulnerability than CVE-2008-6954.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2010-2235
- https://access.redhat.com/errata/RHSA-2010:0775
- https://access.redhat.com/security/cve/CVE-2010-2235
- https://bugzilla.redhat.com/show_bug.cgi?id=607662
- https://github.com/cobbler/cobbler
- https://people.fedoraproject.org/~shenson/cobbler/cobbler-2.0.8.tar.gz
- https://www.redhat.com/support/errata/RHSA-2010-0775.html
