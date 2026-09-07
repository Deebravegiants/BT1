# [M] keycloak-httpd-client-install symlink attack vulnerability

## Summary
Severity: Medium
Advisory: GHSA-vqf9-v3hc-wr54
CVE: CVE-2017-15111
CWE: CWE-59
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-vqf9-v3hc-wr54
Type: github-advisory

## Affected
- PyPI: `keycloak-httpd-client-install` — affected >=0 <0.8

## Details
keycloak-httpd-client-install versions before 0.8 insecurely creates temporary file allowing local attackers to overwrite other files via symbolic link.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-15111
- https://github.com/jdennis/keycloak-httpd-client-install/commit/07f26e213196936fb328ea0c1d5a66a09d8b5440
- https://access.redhat.com/errata/RHSA-2019:2137
- https://github.com/jdennis/keycloak-httpd-client-install
