# [M] KubePi's JWT token validation has a defect

## Summary
Severity: Medium
Advisory: CVE-2024-36111
Aliases: GHSA-8q5r-cvcw-4wx7
CVSS: 6.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L)
Published: 2024-07-25
Source: https://osv.dev/vulnerability/CVE-2024-36111
Type: osv

## Details
KubePi is a K8s panel. Starting in version 1.6.3 and prior to version 1.8.0, there is a defect in the KubePi JWT token verification. The JWT key in the default configuration file is empty. Although a random 32-bit string will be generated to overwrite the key in the configuration file when the key is detected to be empty in the configuration file reading logic, the key is empty during actual verification. Using an empty key to generate a JWT token can bypass the login verification and directly take over the back end. Version 1.8.0 contains a patch for this issue.

## References
- https://github.com/1Panel-dev/KubePi/security/advisories/GHSA-8q5r-cvcw-4wx7
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/36xxx/CVE-2024-36111.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-36111
