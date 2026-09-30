# [C] Overly Permissive Trust Policy in Harmonix on AWS EKS

## Summary
Severity: Critical
Advisory: CVE-2025-14503
Aliases: GHSA-qm86-gqrq-mqcw
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2025-12-15
Source: https://osv.dev/vulnerability/CVE-2025-14503
Type: osv

## Details
An overly-permissive IAM trust policy in the Harmonix on AWS framework may allow IAM principals in the same AWS account to escalate privileges via role assumption. The sample code for the EKS environment provisioning role is configured to trust the account root principal, which may enable any IAM principal in the same AWS account with sts:AssumeRole permissions to assume the role with administrative privileges.


We recommend customers upgrade to Harmonix on AWS v0.4.2 or later if you have deployed the framework using versions v0.3.0 through v0.4.1.

## References
- https://aws.amazon.com/security/security-bulletins/AWS-2025-031/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/14xxx/CVE-2025-14503.json
- https://github.com/awslabs/harmonix/security/advisories/GHSA-qm86-gqrq-mqcw
- https://nvd.nist.gov/vuln/detail/CVE-2025-14503
- https://github.com/awslabs/harmonix/pull/189
