# [M] CVE-2021-3469

## Summary
Severity: Medium
Advisory: CVE-2021-3469
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L)
Published: 2021-06-03
Source: https://osv.dev/vulnerability/CVE-2021-3469
Type: osv

## Details
Foreman versions before 2.3.4 and before 2.4.0 is affected by an improper authorization handling flaw. An authenticated attacker can impersonate the foreman-proxy if product enable the Puppet Certificate authority (CA) to sign certificate requests that have subject alternative names (SANs). Foreman do not enable SANs by default and `allow-authorization-extensions` is set to `false` unless user change `/etc/puppetlabs/puppetserver/conf.d/ca.conf` configuration explicitly.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1943630
