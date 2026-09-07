# [C]  HashiCorp Terraform Amazon Web Services (AWS) uses an insecure PRNG 

## Summary
Severity: Critical
Advisory: GHSA-r48h-jr2j-9g78
CVE: CVE-2018-9057
CWE: CWE-332
Ecosystem: Go
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-r48h-jr2j-9g78
Type: github-advisory

## Affected
- Go: `github.com/hashicorp/terraform-provider-aws` — affected >=0 <1.14.0

## Details
aws/resource_aws_iam_user_login_profile.go in the HashiCorp Terraform Amazon Web Services (AWS) provider through v1.12.0 has an inappropriate PRNG algorithm and seeding, which makes it easier for remote attackers to obtain access by leveraging an IAM account that was provisioned with a weak password.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2018-9057
- https://github.com/hashicorp/terraform-provider-aws/pull/3934
- https://github.com/hashicorp/terraform-provider-aws/pull/3989
- https://github.com/terraform-providers/terraform-provider-aws/pull/3934
- https://github.com/hashicorp/terraform-provider-aws/commit/efa8cd45c6484ff70b2a515ea7ff06f2459d4ddf
- https://github.com/hashicorp/terraform-provider-aws
- https://github.com/hashicorp/terraform-provider-aws/blob/02b039aa82dd7fc6e4a97a0922cc5dbbab724021/resource_aws_iam_user_login_profile.go#L70-L80
