# [C] Ludwig framework is vulnerable to insecure deserialization through its predict() method.

## Summary
Severity: Critical
Advisory: GHSA-wcr3-gm9f-f87q
CVE: CVE-2026-31237
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-12
Source: https://github.com/advisories/GHSA-wcr3-gm9f-f87q
Type: github-advisory

## Affected
- PyPI: `ludwig` — affected >=0

## Details
The Ludwig framework thru 0.10.4 is vulnerable to insecure deserialization (CWE-502) through its predict() method. When a user provides a dataset file path to the predict() method, the framework automatically determines the file format. If the file is a pickle (.pkl) file, it is loaded using pandas.read_pickle() without any validation or security restrictions. This allows the deserialization of arbitrary Python objects via the unsafe pickle module. A remote attacker can exploit this by providing a maliciously crafted pickle file, leading to arbitrary code execution on the system running the Ludwig prediction.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-31237
- https://github.com/ludwig-ai/ludwig
- https://www.notion.so/CVE-2026-31237-35d1e139318881fb95a2ee7c5d0e17d8
