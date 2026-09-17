# [C] conda-forge infrastructure uses a bad token for Azure's cf-staging access

## Summary
Severity: Critical
Advisory: CVE-2025-31484
Aliases: GHSA-m4h2-49xf-vq72
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-04-02
Source: https://osv.dev/vulnerability/CVE-2025-31484
Type: osv

## Details
conda-forge infrastructure holds common configurations and settings for key pieces of the conda-forge infrastructure.
Between 2025-02-10 and 2025-04-01, conda-forge infrastructure used the wrong token for Azure's cf-staging access. This bug meant that any feedstock maintainer could upload a package to the conda-forge channel, bypassing our feedstock-token + upload process. The security logs on anaconda.org were check for any packages that were not copied from the cf-staging to the conda-forge channel and none were found.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/31xxx/CVE-2025-31484.json
- https://github.com/conda-forge/infrastructure/security/advisories/GHSA-m4h2-49xf-vq72
- https://nvd.nist.gov/vuln/detail/CVE-2025-31484
- https://github.com/conda-forge/infrastructure/commit/70f3f09e64968d5f0a7b0525846f17cad42dd052
