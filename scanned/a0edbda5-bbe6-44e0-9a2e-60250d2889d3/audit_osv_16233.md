# [H] CVE-2019-3800

## Summary
Severity: High
Advisory: CVE-2019-3800
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-08-05
Source: https://osv.dev/vulnerability/CVE-2019-3800
Type: osv

## Details
CF CLI version prior to v6.45.0 (bosh release version 1.16.0) writes the client id and secret to its config file when the user authenticates with --client-credentials flag. A local authenticated malicious user with access to the CF CLI config file can act as that client, who is the owner of the leaked credentials.

## References
- https://pivotal.io/security/cve-2019-3800
- https://www.cloudfoundry.org/blog/cve-2019-3800
