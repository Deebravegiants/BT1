# [H] dp-golang Go installation could be owned by wrong user

## Summary
Severity: High
Advisory: CVE-2024-27294
Aliases: GHSA-8h8m-h98f-vv84
CVSS: 7.3 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:L/I:H/A:H)
Published: 2024-02-29
Source: https://osv.dev/vulnerability/CVE-2024-27294
Type: osv

## Details
dp-golang is a Puppet module for Go installations.  Prior to 1.2.7, dp-golang could install files — including the compiler binary — with the wrong ownership when Puppet was run as root and the installed package was On macOS: Go version 1.4.3 through 1.21rc3, inclusive, go1.4-bootstrap-20170518.tar.gz, or go1.4-bootstrap-20170531.tar.gz. The user and group specified in Puppet code were ignored for files within the archive. dp-puppet version 1.2.7 will recreate installations if the owner or group of any file or directory within that installation does not match the requested owner or group

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/27xxx/CVE-2024-27294.json
- https://github.com/danielparks/puppet-golang/security/advisories/GHSA-8h8m-h98f-vv84
- https://nvd.nist.gov/vuln/detail/CVE-2024-27294
- https://github.com/danielparks/puppet-golang/commit/1d0865b24071cb1c00d2fd8cb755d444e6e8f888
- https://github.com/danielparks/puppet-golang/commit/870724a7fef50208515da7bbfa9dfd5d6950e7f5
