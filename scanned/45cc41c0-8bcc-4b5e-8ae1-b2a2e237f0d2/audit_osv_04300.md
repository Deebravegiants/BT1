# [H] Concourse Open Redirect in the /sky/login endpoint

## Summary
Severity: High
Advisory: BIT-concourse-2020-5409
Aliases: CVE-2020-5409
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-concourse-2020-5409
Type: osv

## Affected
- Bitnami: `concourse` — affected >=5.6.0 <5.8.1

## Details
Pivotal Concourse, most versions prior to 6.0.0, allows redirects to untrusted websites in its login flow. A remote unauthenticated attacker could convince a user to click on a link using the OAuth redirect link with an untrusted website and gain access to that user's access token in Concourse. (This issue is similar to, but distinct from, CVE-2018-15798.)

## References
- https://tanzu.vmware.com/security/cve-2020-5409
- https://nvd.nist.gov/vuln/detail/CVE-2020-5409
