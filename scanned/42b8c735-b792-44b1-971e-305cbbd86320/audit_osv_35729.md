# [M] pip absolute path traversal during download from malicious package indexes

## Summary
Severity: Medium
Advisory: CVE-2026-13346
Aliases: GHSA-qwm4-qh6w-59xr, PYSEC-2026-3721
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:H/UI:A/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-07-29
Source: https://osv.dev/vulnerability/CVE-2026-13346
Type: osv

## Details
pip would incorrectly handle doubly-encoded package URLs from indexes allowing for files to be installed to arbitrary locations on disk even when installing wheels.




This vulnerability requires downloading or installing a package from a malicious package index to succeed, malicious packages alone are not able to exploit this vulnerability. Note that this vulnerability only materially impacts users running `pip download` with the `--only-binary` option as installing source distributions from an untrusted index is already an unsafe operation that executes code during install time.

## References
- http://www.openwall.com/lists/oss-security/2026/07/29/7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13346.json
- https://mail.python.org/archives/list/security-announce@python.org/thread/L2BNQGGVQCEV7DROOORQ7WFKKFF2OOQX/
- https://nvd.nist.gov/vuln/detail/CVE-2026-13346
- https://github.com/pypa/pip/pull/14110
- https://github.com/pypa/pip
- https://pypi.org/project/pip
