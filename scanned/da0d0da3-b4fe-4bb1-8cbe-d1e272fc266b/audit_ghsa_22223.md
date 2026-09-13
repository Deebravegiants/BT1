# [C] jsonpickle unsafe deserialization

## Summary
Severity: Critical
Advisory: GHSA-j66q-qmrc-89rx
CVE: CVE-2020-22083
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-j66q-qmrc-89rx
Type: github-advisory

## Affected
- PyPI: `jsonpickle` — affected >=0

## Details
jsonpickle through 1.4.2 allows remote code execution during deserialization of a malicious payload through the `decode()` function. This CVE is disputed by the project author as intended functionality.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-22083
- https://github.com/jsonpickle/jsonpickle/issues/332
- https://github.com/jsonpickle/jsonpickle/issues/332#issuecomment-747807494
- https://github.com/jsonpickle/jsonpickle/issues/335
- https://access.redhat.com/security/cve/CVE-2020-22083
- https://gist.github.com/j0lt-github/bb543e77a1a10c33cb56cf23d0837874
- https://github.com/j0lt-github/python-deserialization-attack-payload-generator
- https://github.com/jsonpickle/jsonpickle
- https://github.com/pypa/advisory-database/tree/main/vulns/jsonpickle/PYSEC-2020-49.yaml
- https://versprite.com/blog/application-security/into-the-jar-jsonpickle-exploitation
