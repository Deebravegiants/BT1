# [M] cross-site inclusion (XSSI) of files in jupyter-server

## Summary
Severity: Medium
Advisory: GHSA-64x5-55rw-9974
CVE: CVE-2023-40170
CWE: CWE-284, CWE-306, CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-08-29
Source: https://github.com/advisories/GHSA-64x5-55rw-9974
Type: github-advisory

## Affected
- PyPI: `jupyter-server` — affected >=0 <2.7.2

## Details
### Impact

Improper cross-site credential checks on `/files/` URLs could allow exposure of certain file contents, or accessing files when opening untrusted files via  "Open image in new tab".

### Patches

Jupyter Server 2.7.2

### Workarounds

Use lower performance `--ContentsManager.files_handler_class=jupyter_server.files.handlers.FilesHandler`, which implements the correct checks.

### References

Upstream patch for CVE-2019-9644 was not applied completely, leaving part of the vulnerability open.

Vulnerability reported by Tim Coen via the [bug bounty program](https://app.intigriti.com/programs/jupyter/jupyter/detail) [sponsored by the European Commission](https://commission.europa.eu/news/european-commissions-open-source-programme-office-starts-bug-bounties-2022-01-19_en) and hosted on the [Intigriti platform](https://www.intigriti.com/).

## References
- https://github.com/jupyter-server/jupyter_server/security/advisories/GHSA-64x5-55rw-9974
- https://nvd.nist.gov/vuln/detail/CVE-2023-40170
- https://github.com/jupyter-server/jupyter_server/commit/87a4927272819f0b1cae1afa4c8c86ee2da002fd
- https://github.com/jupyter-server/jupyter_server
- https://github.com/pypa/advisory-database/tree/main/vulns/jupyter-server/PYSEC-2023-157.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/NRP7DNZYVOIA4ZB3U3ZWKTFZEPYWNGCQ
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/XDKQAWQN6SQTOVACZNXYKEHWQXGG4DOF
