# [H] foreman_kubevirt disables SSL verification if a Certificate Authority (CA) certificate is not explicitly set

## Summary
Severity: High
Advisory: GHSA-2qxw-7fmx-gqfm
CVE: CVE-2026-1531
CWE: CWE-295
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-02-02
Source: https://github.com/advisories/GHSA-2qxw-7fmx-gqfm
Type: github-advisory

## Affected
- RubyGems: `foreman_kubevirt` — affected >=0 <0.4.3

## Details
A flaw was found in foreman_kubevirt. When configuring the connection to OpenShift, the system disables SSL verification if a Certificate Authority (CA) certificate is not explicitly set. This insecure default allows a remote attacker, capable of intercepting network traffic between Satellite and OpenShift, to perform a Man-in-the-Middle (MITM) attack. Such an attack could lead to the disclosure or alteration of sensitive information.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-1531
- https://github.com/theforeman/foreman_kubevirt/commit/6c9973ee59c6fbec65f165eb9ea9dd4ebb6eeef1
- https://access.redhat.com/errata/RHSA-2026:5968
- https://access.redhat.com/errata/RHSA-2026:5970
- https://access.redhat.com/errata/RHSA-2026:5971
- https://access.redhat.com/security/cve/CVE-2026-1531
- https://bugzilla.redhat.com/show_bug.cgi?id=2433786
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/foreman_kubevirt/CVE-2026-1531.yml
- https://github.com/theforeman/foreman_kubevirt
