# [C] Loaded Databook of Tablib prone to python insertion resulting in command execution

## Summary
Severity: Critical
Advisory: GHSA-gcr6-rf47-jrgf
CVE: CVE-2017-2810
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-13
Source: https://github.com/advisories/GHSA-gcr6-rf47-jrgf
Type: github-advisory

## Affected
- PyPI: `tablib` — affected >=0 <0.11.5

## Details
An exploitable vulnerability exists in the Databook loading functionality of Tablib 0.11.4. A yaml loaded Databook can execute arbitrary python commands resulting in command execution. An attacker can insert python into loaded yaml to trigger this vulnerability.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-2810
- https://github.com/jazzband/tablib/commit/69abfc3ada5d754cb152119c0b4777043657cb6e
- https://github.com/advisories/GHSA-gcr6-rf47-jrgf
- https://github.com/jazzband/tablib
- https://github.com/pypa/advisory-database/tree/main/vulns/tablib/PYSEC-2017-95.yaml
- https://security.gentoo.org/glsa/201811-18
- https://talosintelligence.com/vulnerability_reports/TALOS-2017-0307
