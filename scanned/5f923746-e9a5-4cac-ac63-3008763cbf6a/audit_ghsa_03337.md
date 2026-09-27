# [M] mongodb-client-encryption vulnerable to Improper Certificate Validation

## Summary
Severity: Medium
Advisory: GHSA-rjmf-p882-645m
CVE: CVE-2021-20327
CWE: CWE-295
Ecosystem: npm
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-04-12
Source: https://github.com/advisories/GHSA-rjmf-p882-645m
Type: github-advisory

## Affected
- npm: `mongodb-client-encryption` — affected >=1.2.0 <1.2.1

## Details
A specific version of the Node.js mongodb-client-encryption module does not perform correct validation of the KMS server’s certificate. This vulnerability in combination with a privileged network position active MITM attack could result in interception of traffic between the Node.js driver and the KMS service rendering client-side field level encryption (CSFLE) ineffective. This issue was discovered during internal testing and affects mongodb-client-encryption module version 1.2.0, which was available from 2021-Jan-29 and deprecated in the NPM Registry on 2021-Feb-04. This vulnerability does not impact driver traffic payloads with CSFLE-supported key services from applications residing inside the AWS, GCP, and Azure nework fabrics due to compensating controls in these environments. This issue does not impact driver workloads that don’t use Field Level Encryption. This issue affect MongoDB Node.js Driver mongodb-client-encryption module version 1.2.0

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-20327
- https://github.com/mongodb/libmongocrypt/commit/76365515ff8754b9f705e56428dd0d7efa7f541b
- https://github.com/mongodb/libmongocrypt
- https://jira.mongodb.org/browse/NODE-3125
- https://www.npmjs.com/advisories/1660
