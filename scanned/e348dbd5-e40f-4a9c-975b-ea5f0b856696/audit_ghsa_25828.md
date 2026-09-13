# [H] Improper Certificate Validation in kubeclient

## Summary
Severity: High
Advisory: GHSA-69p3-xp37-f692
CVE: CVE-2022-0759
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-03-26
Source: https://github.com/advisories/GHSA-69p3-xp37-f692
Type: github-advisory

## Affected
- RubyGems: `kubeclient` — affected >=0 <4.9.3

## Details
A flaw was found in all versions of kubeclient up to (but not including) v4.9.3, the Ruby client for Kubernetes REST API, in the way it parsed kubeconfig files. When the kubeconfig file does not configure custom CA to verify certs, kubeclient ends up accepting any certificate (it wrongly returns VERIFY_NONE). Ruby applications that leverage kubeclient to parse kubeconfig files are susceptible to Man-in-the-middle attacks (MITM).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-0759
- https://github.com/ManageIQ/kubeclient/issues/554
- https://github.com/ManageIQ/kubeclient/issues/555
- https://github.com/ManageIQ/kubeclient/pull/556
- https://github.com/ManageIQ/kubeclient/commit/109ea71de5a8881748f03ebbe103b49f0f1c7887
- https://github.com/ManageIQ/kubeclient
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/kubeclient/CVE-2022-0759.yml
