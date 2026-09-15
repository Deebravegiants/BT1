# [C] RCE in the package conda-forge-metadata

## Summary
Severity: Critical
Advisory: CVE-2025-27510
Aliases: GHSA-vwfh-m3q7-9jpw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-03-04
Source: https://osv.dev/vulnerability/CVE-2025-27510
Type: osv

## Details
conda-forge-metadata provides programatic access to conda-forge's metadata. conda-forge-metadata uses an optional dependency - "conda-oci-mirror" which was neither present on the PyPi repository nor registered by any entity. If conda-oci-mirror is taken over by a threat actor, it can result in remote code execution.

## References
- https://github.com/conda-forge/conda-forge-metadata/blob/799aee36b21ee06289d73d57838b28201f5a57af/pyproject.toml#L28
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/27xxx/CVE-2025-27510.json
- https://github.com/conda-forge/conda-forge-metadata/security/advisories/GHSA-vwfh-m3q7-9jpw
- https://nvd.nist.gov/vuln/detail/CVE-2025-27510
