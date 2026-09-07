# [M] jupyter-server errors include tracebacks with path information

## Summary
Severity: Medium
Advisory: GHSA-h56g-gq9v-vc8r
CVE: CVE-2023-49080
CWE: CWE-209
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-h56g-gq9v-vc8r
Type: github-advisory

## Affected
- PyPI: `jupyter-server` — affected >=0 <2.11.2

## Details
### Impact

Unhandled errors in API requests include traceback information, which can include path information. There is no known mechanism by which to trigger these errors without authentication, so the paths revealed are not considered particularly sensitive, given that the requesting user has arbitrary execution permissions already in the same environment.

### Patches

jupyter-server PATCHED_VERSION no longer includes traceback information in JSON error responses. For compatibility, the traceback field is present, but always empty.

### Workarounds

None

## References
- https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-h56g-gq9v-vc8r
- https://nvd.nist.gov/vuln/detail/CVE-2023-49080
- https://github.com/jupyter-server/jupyter_server/commit/0056c3aa52cbb28b263a7a609ae5f17618b36652
- https://github.com/jupyter-server/jupyter_server
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2023-272.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/62LO7PPIAMLIDEKUOORXLHKLGA6QPL77
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/FG2JWZI5KPUYMDPS53AIFTZJWZD3IT6I
