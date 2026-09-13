# [H] Uncaught Exception (due to a data race) leads to process termination in Waitress

## Summary
Severity: High
Advisory: GHSA-f5x9-8jwc-25rw
CVE: CVE-2022-31015
CWE: CWE-248, CWE-362
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-02
Source: https://github.com/advisories/GHSA-f5x9-8jwc-25rw
Type: github-advisory

## Affected
- PyPI: `waitress` — affected >=2.1.0 <2.1.2

## Details
### Impact

Waitress may terminate early due to a thread closing a socket while the main thread is about to call select(). This will lead to the main thread raising an exception that is not handled and then causing the entire application to be killed.

### Patches

This issue has been fixed in Waitress 2.1.2 by no longer allowing the WSGI thread to close the socket, instead it is always delegated to the main thread.

### Workarounds

There is no work-around, however users using waitress behind a reverse proxy server are less likely to have issues if the reverse proxy always reads the full response.

### For more information

If you have any questions or comments about this advisory:
* Open an issue in https://github.com/Pylons/waitress/issues (if not sensitive or security related)
* email the Pylons Security mailing list: [pylons-project-security@googlegroups.com](mailto:pylons-project-security@googlegroups.com) (if security related)

## References
- https://github.com/Pylons/waitress/security/advisories/GHSA-f5x9-8jwc-25rw
- https://nvd.nist.gov/vuln/detail/CVE-2022-31015
- https://github.com/Pylons/waitress/issues/374
- https://github.com/Pylons/waitress/pull/377
- https://github.com/Pylons/waitress/commit/4f6789b035610e0552738cdc4b35ca809a592d48
- https://github.com/Pylons/waitress
- https://github.com/pypa/advisory-database/tree/main/vulns/waitress/PYSEC-2022-205.yaml
