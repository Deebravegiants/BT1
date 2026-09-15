# [M] docarray prototype pollution

## Summary
Severity: Medium
Advisory: GHSA-j9wp-865g-rf48
CVE: CVE-2025-5150
CWE: CWE-1321, CWE-94
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-05-25
Source: https://github.com/advisories/GHSA-j9wp-865g-rf48
Type: github-advisory

## Affected
- PyPI: `docarray` — affected >=0

## Details
A vulnerability was found in docarray up to 0.40.1. It has been rated as critical. Affected by this issue is the function __getitem__ of the file /docarray/data/torch_dataset.py of the component Web API. The manipulation leads to improperly controlled modification of object prototype attributes ('prototype pollution'). The attack may be launched remotely. The exploit has been disclosed to the public and may be used. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-5150
- https://gist.github.com/superboy-zjc/56502343bcb12eb653081b426debf2c8
- https://github.com/docarray/docarray
- https://vuldb.com/?ctiid.310238
- https://vuldb.com/?id.310238
- https://vuldb.com/?submit.574696
