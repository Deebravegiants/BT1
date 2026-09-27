# [M] BIT-gitlab-2021-39899

## Summary
Severity: Medium
Advisory: BIT-gitlab-2021-39899
Aliases: CVE-2021-39899
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-gitlab-2021-39899
Type: osv

## Affected
- Bitnami: `gitlab` — affected >=14.3.0 <14.3.1

## Details
In all versions of GitLab CE/EE, an attacker with physical access to a user’s machine may brute force the user’s password via the change password function. There is a rate limit in place, but the attack may still be conducted by stealing the session id from the physical compromise of the account and splitting the attack over several IP addresses and passing in the compromised session value from these various locations.

## References
- https://gitlab.com/gitlab-org/cves/-/blob/master/2021/CVE-2021-39899.json
- https://gitlab.com/gitlab-org/gitlab/-/issues/339154
- https://nvd.nist.gov/vuln/detail/CVE-2021-39899
