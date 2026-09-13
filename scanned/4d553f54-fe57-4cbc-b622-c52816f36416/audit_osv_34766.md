# [C] Typebot May Expose AWS EKS Credentials via Server Side Request Forgery in Webhook Block

## Summary
Severity: Critical
Advisory: CVE-2025-64709
Aliases: GHSA-8gq9-rw7v-3jpr
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N)
Published: 2025-11-13
Source: https://osv.dev/vulnerability/CVE-2025-64709
Type: osv

## Details
Typebot is an open-source chatbot builder. In versions prior to 3.13.1, a Server-Side Request Forgery (SSRF) vulnerability in the Typebot webhook block (HTTP Request component) functionality allows authenticated users to make arbitrary HTTP requests from the server, including access to AWS Instance Metadata Service (IMDS). By bypassing IMDSv2 protection through custom header injection, attackers can extract temporary AWS IAM credentials for the EKS node role, leading to complete compromise of the Kubernetes cluster and associated AWS infrastructure. Version 3.13.1 fixes the issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/64xxx/CVE-2025-64709.json
- https://github.com/baptisteArno/typebot.io/security/advisories/GHSA-8gq9-rw7v-3jpr
- https://nvd.nist.gov/vuln/detail/CVE-2025-64709
