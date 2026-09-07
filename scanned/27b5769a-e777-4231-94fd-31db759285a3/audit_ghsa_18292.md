# [M] ml-logger file handler allows reading arbitrary files

## Summary
Severity: Medium
Advisory: GHSA-9x36-c74v-fgr6
CVE: CVE-2025-10952
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2025-09-25
Source: https://github.com/advisories/GHSA-9x36-c74v-fgr6
Type: github-advisory

## Affected
- PyPI: `ml-logger` — affected >=0

## Details
A security flaw has been discovered in geyang ml-logger up to acf255bade5be6ad88d90735c8367b28cbe3a743. Affected by this issue is the function stream_handler of the file ml_logger/server.py of the component File Handler. Performing manipulation of the argument key results in information disclosure. The attack can be initiated remotely. The exploit has been released to the public and may be exploited. Continious delivery with rolling releases is used by this product. Therefore, no version details of affected nor updated releases are available.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10952
- https://github.com/geyang/ml-logger/issues/74
- https://github.com/geyang/ml-logger
- https://vuldb.com/?ctiid.325822
- https://vuldb.com/?id.325822
- https://vuldb.com/?submit.652463
