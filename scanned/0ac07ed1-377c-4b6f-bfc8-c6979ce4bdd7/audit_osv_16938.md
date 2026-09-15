# [H] CVE-2020-10758

## Summary
Severity: High
Advisory: CVE-2020-10758
Aliases: GHSA-52rg-hpwq-qp56
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-09-16
Source: https://osv.dev/vulnerability/CVE-2020-10758
Type: osv

## Details
A vulnerability was found in Keycloak before 11.0.1 where DoS attack is possible by sending twenty requests simultaneously to the specified keycloak server, all with a Content-Length header value that exceeds the actual byte count of the request body.

## References
- https://bugzilla.redhat.com/show_bug.cgi?id=1843849
- https://github.com/keycloak/keycloak/commit/bee4ca89897766c4b68856eafe14f1a3dad34251
