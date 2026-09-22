# [C] Shinken Solutions Shinken Monitoring vulnerable to Incorrect Access Control

## Summary
Severity: Critical
Advisory: GHSA-p373-jqfm-j6wr
CVE: CVE-2022-37298
CWE: CWE-287
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-10-20
Source: https://github.com/advisories/GHSA-p373-jqfm-j6wr
Type: github-advisory

## Affected
- PyPI: `Shinken` — affected >=0

## Details
Shinken Solutions Shinken Monitoring Version 2.4.3 affected is vulnerable to Incorrect Access Control. The `SafeUnpickler` class found in `shinken/safepickle.py` implements a weak authentication scheme when unserializing objects passed from monitoring nodes to the Shinken monitoring server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-37298
- https://github.com/naparuba/shinken/commit/2dae40fd1e713aec9e1966a0ab7a580b9180cff2
- https://github.com/dbyio/cve-2022-37298
- https://github.com/naparuba/shinken
