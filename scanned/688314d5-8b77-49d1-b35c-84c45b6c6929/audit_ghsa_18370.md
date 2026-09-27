# [M] SGLang Remote Code Execution Vulnerability via Unsafe Deserialization in update_weights_from_tensor

## Summary
Severity: Medium
Advisory: GHSA-9w53-xr52-mwgj
CVE: CVE-2025-10164
CWE: CWE-20, CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-9w53-xr52-mwgj
Type: github-advisory

## Affected
- PyPI: `sglang` — affected >=0 <0.5.4

## Details
A security flaw has been discovered in lmsys sglang 0.4.6. Affected by this vulnerability is the function main of the file /update_weights_from_tensor. The manipulation of the argument serialized_named_tensors results in deserialization. The attack can be launched remotely. The exploit has been released to the public and may be exploited. The vendor was contacted early about this disclosure but did not respond in any way.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10164
- https://github.com/sgl-project/sglang/commit/49afb3d9d9deedf6dea3a6dd5c50e85e7d8bcb07
- https://github.com/sgl-project/sglang
- https://vuldb.com/?ctiid.323203
- https://vuldb.com/?id.323203
- https://vuldb.com/?submit.635919
