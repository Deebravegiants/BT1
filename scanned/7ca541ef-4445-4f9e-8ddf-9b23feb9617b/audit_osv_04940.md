# [H] BIT-gitlab-2020-13298

## Summary
Severity: High
Advisory: BIT-gitlab-2020-13298
Aliases: CVE-2020-13298
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2020-13298
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=13.3.0 <13.3.4

## Details
A vulnerability was discovered in GitLab versions before 13.1.10, 13.2.8 and 13.3.4. Conan package upload functionality was not properly validating the supplied parameters, which resulted in the limited files disclosure.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2020/CVE-2020-13298.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/228841
- https://hackerone.com/reports/923027
- https://nvd.nist.gov/vuln/detail/CVE-2020-13298
