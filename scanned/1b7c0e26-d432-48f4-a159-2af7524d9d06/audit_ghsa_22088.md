# [H] SaltStack Salt Denial of Service via a crafted authentication request

## Summary
Severity: High
Advisory: GHSA-657p-cj5r-mjrh
CVE: CVE-2017-14696
CWE: CWE-20, CWE-400
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-657p-cj5r-mjrh
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=0 <2016.3.8
- PyPI: `salt` — affected >=2016.11.0 <2016.11.8
- PyPI: `salt` — affected >=2017.7.0 <2017.7.2

## Details
SaltStack Salt before 2016.3.8, 2016.11.x before 2016.11.8, and 2017.7.x before 2017.7.2 allows remote attackers to cause a denial of service via a crafted authentication request.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-14696
- https://github.com/saltstack/salt/commit/5f8b5e1a0f23fe0f2be5b3c3e04199b57a53db5b
- https://bugzilla.redhat.com/show_bug.cgi?id=1500742
- https://docs.saltstack.com/en/latest/topics/releases/2016.11.8.html
- https://docs.saltstack.com/en/latest/topics/releases/2016.3.8.html
- https://docs.saltstack.com/en/latest/topics/releases/2017.7.2.html
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2017-37.yaml
- https://github.com/saltstack/salt
- http://lists.opensuse.org/opensuse-updates/2017-10/msg00073.html
- http://lists.opensuse.org/opensuse-updates/2017-10/msg00075.html
