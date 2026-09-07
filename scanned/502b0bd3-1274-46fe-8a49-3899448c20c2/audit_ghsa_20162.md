# [C] Unsafe yaml deserialization in NVFlare

## Summary
Severity: Critical
Advisory: GHSA-hrf3-622q-8366
CVE: CVE-2022-31605
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-06-22
Source: https://github.com/advisories/GHSA-hrf3-622q-8366
Type: github-advisory

## Affected
- PyPI: `nvflare` — affected >=0 <2.1.2

## Details
### Impact
NVFLARE contains a vulnerability in its utils module, where YAML files are loaded via yaml.load() instead of yaml.safe_load(). The deserialization of Untrusted Data, may allow an unprivileged network attacker to cause Remote Code Execution, Denial Of Service, and Impact to both Confidentiality and Integrity.

All versions before 2.1.2 are affected.
CVSS Score = 9.8
[AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H](https://nam11.safelinks.protection.outlook.com/?url=https%3A%2F%2Fnvd.nist.gov%2Fvuln-metrics%2Fcvss%2Fv3-calculator%3Fvector%3DAV%3AN%2FAC%3AL%2FPR%3AN%2FUI%3AN%2FS%3AU%2FC%3AH%2FI%3AH%2FA%3AH&data=05%7C01%7Cchesterc%40nvidia.com%7Ce9600bde16854b0b380008da4fc544f7%7C43083d15727340c1b7db39efd9ccc17a%7C0%7C0%7C637910005925574215%7CUnknown%7CTWFpbGZsb3d8eyJWIjoiMC4wLjAwMDAiLCJQIjoiV2luMzIiLCJBTiI6Ik1haWwiLCJXVCI6Mn0%3D%7C3000%7C%7C%7C&sdata=5kBrXEmAbqp8R31JCH%2FG95MUly72UPVihnBwiRFmvBY%3D&reserved=0)


### Patches

The patch will be included in nvflare==2.1.2


### Workarounds
Change yaml.load() to yaml.safe_load()

### Additional information
Issue Found by: Oliver Sellwood (@Nintorac)

## References
- https://github.com/NVIDIA/NVFlare/security/advisories/GHSA-hrf3-622q-8366
- https://nvd.nist.gov/vuln/detail/CVE-2022-31605
- https://github.com/NVIDIA/NVFlare/commit/4de9782697ecb12f39bcae83221bd8d3498959be
- https://github.com/NVIDIA/NVFlare
- https://github.com/pypa/advisory-database/tree/main/vulns/nvflare/PYSEC-2022-232.yaml
