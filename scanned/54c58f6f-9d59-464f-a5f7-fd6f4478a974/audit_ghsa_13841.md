# [M] Exposure of Sensitive Information in EVE-SRP

## Summary
Severity: Medium
Advisory: GHSA-fxqx-xgqq-gf42
CVE: CVE-2020-36660
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-02-06
Source: https://github.com/advisories/GHSA-fxqx-xgqq-gf42
Type: github-advisory

## Affected
- PyPI: `EVE-SRP` — affected >=0 <0.12.12

## Details
A vulnerability was found in paxswill EVE Ship Replacement Program 0.12.11. It has been rated as problematic. This issue affects some unknown processing of the file src/evesrp/views/api.py of the component User Information Handler. The manipulation leads to information disclosure. The attack may be initiated remotely. Upgrading to version 0.12.12 is able to address this issue. The name of the patch is 9e03f68e46e85ca9c9694a6971859b3ee66f0240. It is recommended to upgrade the affected component. The associated identifier of this vulnerability is VDB-220211.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-36660
- https://github.com/paxswill/evesrp/commit/9e03f68e46e85ca9c9694a6971859b3ee66f0240
- https://github.com/paxswill/evesrp
- https://github.com/paxswill/evesrp/releases/tag/v0.12.12
- https://github.com/pypa/advisory-database/tree/main/vulns/eve-srp/PYSEC-2023-208.yaml
- https://vuldb.com/?ctiid.220211
- https://vuldb.com/?id.220211
