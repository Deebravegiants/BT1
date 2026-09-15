# [C] conda-forge-webservices has an Unauthorized Artifact Modification Race Condition

## Summary
Severity: Critical
Advisory: CVE-2025-32784
Aliases: GHSA-28cx-74fp-g2g2
CVSS: 9.0 (CVSS:4.0/AV:N/AC:H/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-04-15
Source: https://osv.dev/vulnerability/CVE-2025-32784
Type: osv

## Details
conda-forge-webservices is the web app deployed to run conda-forge admin commands and linting. In versions prior to 2025.4.10, a race condition vulnerability has been identified in the conda-forge-webservices component used within the shared build infrastructure. This vulnerability, categorized as a Time-of-Check to Time-of-Use (TOCTOU) issue, can be exploited to introduce unauthorized modifications to build artifacts stored in the cf-staging Anaconda channel. Exploitation may result in the unauthorized publication of malicious artifacts to the production conda-forge channel. The core vulnerability results from the absence of atomicity between the hash validation and the artifact copy operation. This gap allows an attacker, with access to the cf-staging token, to overwrite the validated artifact with a malicious version immediately after hash verification, but before the copy action is executed. As the cf-staging channel permits artifact overwrites, such an operation can be carried out using the anaconda upload --force command. This vulnerability is fixed in 2025.4.10.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/32xxx/CVE-2025-32784.json
- https://github.com/conda-forge/conda-forge-webservices/security/advisories/GHSA-28cx-74fp-g2g2
- https://nvd.nist.gov/vuln/detail/CVE-2025-32784
- https://github.com/conda-forge/conda-forge-webservices/commit/141ed27617068debd150956341551df3a5a3807d
