# [H] Allocation of Resources Without Limits or Throttling in nvflare

## Summary
Severity: High
Advisory: GHSA-jx8f-cpx7-fv47
CVE: CVE-2022-21822
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-03-18
Source: https://github.com/advisories/GHSA-jx8f-cpx7-fv47
Type: github-advisory

## Affected
- PyPI: `nvflare` — affected >=0 <2.0.16

## Details
### Impact
NVIDIA FLARE contains a vulnerability in Admin Interface, where an un-authorized attacker can cause Allocation of Resources Without Limits or Throttling, which may lead to cause system unavailable

All versions before 2.0.16 are affected.

### Patches
The patch will be included in nvflare==2.0.16.

### Workarounds
The changes in commits https://github.com/NVIDIA/NVFlare/commit/93588b3a0dff9bd4568983071b74d8b420de3a6e and https://github.com/NVIDIA/NVFlare/commit/93588b3a0dff9bd4568983071b74d8b420de3a6e  can be applied to any version of the NVIDIA FLARE without any adverse effect.

### Additional information
Issue Found on: 2022.3.3
Issue Found by: Oliver Sellwood (@Nintorac)

## References
- https://github.com/NVIDIA/NVFlare/security/advisories/GHSA-jx8f-cpx7-fv47
- https://nvd.nist.gov/vuln/detail/CVE-2022-21822
- https://github.com/NVIDIA/NVFlare
