# [M] Deserialization of Untrusted Data in parlai

## Summary
Severity: Medium
Advisory: GHSA-m87f-9fvv-2mgg
CVE: CVE-2021-39207
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2021-09-13
Source: https://github.com/advisories/GHSA-m87f-9fvv-2mgg
Type: github-advisory

## Affected
- PyPI: `parlai` — affected >=0 <1.1.0

## Details
### Impact
Due to use of unsafe YAML deserialization logic, an attacker with the ability to modify local YAML configuration files could provide malicious input, resulting in remote code execution or similar risks.

### Patches
The issue can be patched by upgrading to v1.1.0 or later. It can also be patched by replacing YAML deserialization with equivalent safe_load calls.

### References

- https://github.com/facebookresearch/ParlAI/commit/507d066ef432ea27d3e201da08009872a2f37725
- https://github.com/facebookresearch/ParlAI/commit/4374fa2aba383db6526ab36e939eb1cf8ef99879
- https://anon-artist.github.io/blogs/blog3.html

## References
- https://github.com/facebookresearch/ParlAI/security/advisories/GHSA-m87f-9fvv-2mgg
- https://nvd.nist.gov/vuln/detail/CVE-2021-39207
- https://github.com/facebookresearch/ParlAI/commit/4374fa2aba383db6526ab36e939eb1cf8ef99879
- https://github.com/facebookresearch/ParlAI/commit/507d066ef432ea27d3e201da08009872a2f37725
- https://github.com/advisories/GHSA-mwgj-7x7j-6966
- https://github.com/facebookresearch/ParlAI
- https://github.com/facebookresearch/ParlAI/releases/tag/v1.1.0
- https://github.com/pypa/advisory-database/tree/main/vulns/parlai/PYSEC-2021-330.yaml
- https://github.com/pypa/advisory-database/tree/main/vulns/parlai/PYSEC-2021-334.yaml
- http://packetstormsecurity.com/files/164136/Facebook-ParlAI-1.0.0-Code-Execution-Deserialization.html
