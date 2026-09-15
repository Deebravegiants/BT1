# [C] OpenStack Murano Code Execution

## Summary
Severity: Critical
Advisory: GHSA-87r7-q54j-f9qg
CVE: CVE-2016-4972
CWE: CWE-20
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-87r7-q54j-f9qg
Type: github-advisory

## Affected
- PyPI: `murano` — affected >=0 <1.0.3
- PyPI: `murano-dashboard` — affected >=0 <1.0.3
- PyPI: `murano-dashboard` — affected >=2.0.0 <2.0.1
- PyPI: `python-muranoclient` — affected >=0 <0.7.3
- PyPI: `python-muranoclient` — affected >=0.8.0 <0.8.5

## Details
OpenStack Murano before 1.0.3 (liberty) and 2.x before 2.0.1 (mitaka), Murano-dashboard before 1.0.3 (liberty) and 2.x before 2.0.1 (mitaka), and python-muranoclient before 0.7.3 (liberty) and 0.8.x before 0.8.5 (mitaka) improperly use loaders inherited from yaml.Loader when parsing MuranoPL and UI files, which allows remote attackers to create arbitrary Python objects and execute arbitrary code via crafted extended YAML tags in UI definitions in packages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-4972
- https://github.com/openstack/murano/commit/28de8c36c9dbe4aaf4d062e6fb6099afd437f49b
- https://bugs.launchpad.net/murano/+bug/1586079
- https://bugs.launchpad.net/python-muranoclient/+bug/1586078
- https://github.com/openstack/murano
- https://github.com/openstack/murano/blob/c898a310afbc27f12190446ef75d8b0bd12115eb/releasenotes/notes/safeloader-cve-2016-4972-19035a2a091ec30a.yaml
- https://github.com/openstack/murano/blob/c898a310afbc27f12190446ef75d8b0bd12115eb/releasenotes/source/locale/en_GB/LC_MESSAGES/releasenotes.po
- https://github.com/pypa/advisory-database/tree/main/vulns/python-muranoclient/PYSEC-2016-22.yaml
- http://www.openwall.com/lists/oss-security/2016/06/23/8
