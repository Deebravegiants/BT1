# [C] nixos/mysql : `services.mysql` is configured with insecure authentication by default when used with `mysql` or `percona-server`

## Summary
Severity: Critical
Advisory: CVE-2026-61828
Aliases: GHSA-6qxx-6rg8-c4p8
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-15
Source: https://osv.dev/vulnerability/CVE-2026-61828
Type: osv

## Details
Nixpkgs is a collection of software packages that can be installed with the Nix package manager. Prior to the 25.11 and 26.05 channel fixes, the NixOS module for MySQL services.mysql initializes the MySQL database in a way that allows local users, such as unprivileged web or CGI processes on the same host, to log in as the root user without a password when the service is used with mysql or percona-server. This issue is fixed in the 25.11 and 26.05.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/61xxx/CVE-2026-61828.json
- https://github.com/NixOS/nixpkgs/security/advisories/GHSA-6qxx-6rg8-c4p8
- https://nvd.nist.gov/vuln/detail/CVE-2026-61828
- https://github.com/NixOS/nixpkgs/commit/3f68d7ad2a6865ff8b4910d89f173d7258bad8dd
- https://github.com/NixOS/nixpkgs/commit/4aed47116a8734922763cd8f477467b0a0bcd6d7
- https://github.com/NixOS/nixpkgs/commit/f8ee41468a7a8f9ed3a8cc7d017151c2ca6f90b5
- https://github.com/NixOS/nixpkgs/pull/534254
- https://github.com/NixOS/nixpkgs/pull/534482
- https://github.com/NixOS/nixpkgs/pull/534484
