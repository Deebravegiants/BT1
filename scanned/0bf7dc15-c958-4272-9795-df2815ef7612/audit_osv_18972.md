# [H] CVE-2020-5399

## Summary
Severity: High
Advisory: CVE-2020-5399
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-02-12
Source: https://osv.dev/vulnerability/CVE-2020-5399
Type: osv

## Details
Cloud Foundry CredHub, versions prior to 2.5.10, connects to a MySQL database without TLS even when configured to use TLS. A malicious user with access to the network between CredHub and its MySQL database may eavesdrop on database connections and thereby gain unauthorized access to CredHub and other components.

## References
- https://www.cloudfoundry.org/blog/cve-2020-5399
