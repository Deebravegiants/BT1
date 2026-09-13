# [C] salt password information leaked in debug logs

## Summary
Severity: Critical
Advisory: GHSA-cxm4-7qcw-267r
CVE: CVE-2015-6941
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-cxm4-7qcw-267r
Type: github-advisory

## Affected
- PyPI: `salt` — affected >=2015.5 <2015.5.6
- PyPI: `salt` — affected >=2015.8 <2015.8.1

## Details
win_useradd, salt-cloud and the Linode driver in salt 2015.5.x before 2015.5.6, and 2015.8.x before 2015.8.1 leak password information in debug logs.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2015-6941
- https://github.com/saltstack/salt/commit/c0689e32154c41f59840ae10ffc5fbfa30618710
- https://github.com/saltstack/salt/commit/fdd35374562658f4a20767a3703fab93d92f9ca9
- https://github.com/twangboy/salt/commit/c0689e32154c41f59840ae10ffc5fbfa30618710
- https://bugzilla.redhat.com/show_bug.cgi?id=1273066
- https://docs.saltstack.com/en/latest/topics/releases/2015.5.6.html
- https://docs.saltstack.com/en/latest/topics/releases/2015.8.1.html
- https://github.com/pypa/advisory-database/tree/main/vulns/salt/PYSEC-2017-71.yaml
- https://github.com/saltstack/salt
