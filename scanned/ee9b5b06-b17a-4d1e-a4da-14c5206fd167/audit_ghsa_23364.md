# [H] Borg Improper Access Control vulnerability

## Summary
Severity: High
Advisory: GHSA-8q8v-28rm-qw4w
CVE: CVE-2017-15914
CWE: CWE-284
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-8q8v-28rm-qw4w
Type: github-advisory

## Affected
- PyPI: `borgbackup` — affected >=1.1.0b1 <1.1.3

## Details
Incorrect implementation of access controls allows remote users to override repository restrictions in Borg servers 1.1.x before 1.1.3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15914
- https://github.com/borgbackup/borg/commit/75854c1243b29ec5558be6fdefe365cd438abb4c
- https://github.com/borgbackup/borg
- https://github.com/pypa/advisory-database/tree/main/vulns/borgbackup/PYSEC-2018-105.yaml
- http://borgbackup.readthedocs.io/en/stable/changes.html#version-1-1-3-2017-11-27
