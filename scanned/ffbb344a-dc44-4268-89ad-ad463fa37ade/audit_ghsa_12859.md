# [H] NYUCCL psiTurk IS vulnerable to Improper Neutralization of Special Elements

## Summary
Severity: High
Advisory: GHSA-9mq4-9556-6qxq
CVE: CVE-2021-4315
CWE: CWE-1336, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-01-29
Source: https://github.com/advisories/GHSA-9mq4-9556-6qxq
Type: github-advisory

## Affected
- PyPI: `psiTurk` — affected >=0 <3.2.1

## Details
A vulnerability has been found in NYUCCL psiTurk up to 3.2.0 and classified as critical. This vulnerability affects unknown code of the file psiturk/experiment.py. The manipulation of the argument mode leads to improper neutralization of special elements used in a template engine. The exploit has been disclosed to the public and may be used. Upgrading to version 3.2.1 is able to address this issue. The name of the patch is 47787e15cecd66f2aa87687bf852ae0194a4335f. It is recommended to upgrade the affected component. The identifier of this vulnerability is VDB-219676.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4315
- https://github.com/NYUCCL/psiTurk/pull/517
- https://github.com/NYUCCL/psiTurk/commit/47787e15cecd66f2aa87687bf852ae0194a4335f
- https://github.com/NYUCCL/psiTurk
- https://github.com/NYUCCL/psiTurk/releases/tag/v3.2.1
- https://github.com/pypa/advisory-database/tree/main/vulns/psiturk/PYSEC-2023-43.yaml
- https://vuldb.com/?ctiid.219676
- https://vuldb.com/?id.219676
