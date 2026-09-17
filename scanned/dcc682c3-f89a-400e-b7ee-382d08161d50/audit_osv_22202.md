# [M] Spinnaker's Rosco microservice vulnerable to improper log masking on AWS Packer builds

## Summary
Severity: Medium
Advisory: CVE-2022-23506
Aliases: GHSA-2233-cqj8-j2q5
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-01-03
Source: https://osv.dev/vulnerability/CVE-2022-23506
Type: osv

## Details
Spinnaker is an open source, multi-cloud continuous delivery platform for releasing software changes, and Spinnaker's Rosco microservice produces machine images. Rosco prior to versions 1.29.2, 1.28.4, and 1.27.3 does not property mask secrets generated via packer builds.  This can lead to exposure of sensitive AWS credentials in packer log files. Versions 1.29.2, 1.28.4, and 1.27.3 of Rosco contain fixes for this issue.

A workaround is available. It's recommended to use short lived credentials via role assumption and IAM profiles. Additionally, credentials can be set in `/home/spinnaker/.aws/credentials` and `/home/spinnaker/.aws/config` as a volume mount for Rosco pods vs. setting credentials in roscos bake config properties. Last even with those it's recommend to use IAM Roles vs. long lived credentials. This drastically mitigates the risk of credentials exposure. If users have used static credentials, it's recommended to purge any bake logs for AWS, evaluate whether AWS_ACCESS_KEY, SECRET_KEY and/or other sensitive data has been introduced in log files and bake job logs. Then, rotate these credentials and evaluate potential improper use of those credentials.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/23xxx/CVE-2022-23506.json
- https://github.com/spinnaker/spinnaker/security/advisories/GHSA-2233-cqj8-j2q5
- https://nvd.nist.gov/vuln/detail/CVE-2022-23506
- https://github.com/spinnaker/rosco/commit/e80cfaa1abfb3a0e9026d45d6027291bfb815daf
