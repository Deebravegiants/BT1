# [H] Remote unauthenticated denial-of-service in Subversion mod_authz_svn

## Summary
Severity: High
Advisory: BIT-subversion-2020-17525
Aliases: CVE-2020-17525
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-subversion-2020-17525
Type: osv

## Affected
- Bitnami: `subversion` — affected >=1.11.0 <1.14.1

## Details
Subversion's mod_authz_svn module will crash if the server is using in-repository authz rules with the AuthzSVNReposRelativeAccessFile option and a client sends a request for a non-existing repository URL. This can lead to disruption for users of the service. This issue was fixed in mod_dav_svn+mod_authz_svn servers 1.14.1 and mod_dav_svn+mod_authz_svn servers 1.10.7

## References
- https://lists.debian.org/debian-lts-announce/2021/05/msg00000.html
- https://subversion.apache.org/security/CVE-2020-17525-advisory.txt
- https://nvd.nist.gov/vuln/detail/CVE-2020-17525
