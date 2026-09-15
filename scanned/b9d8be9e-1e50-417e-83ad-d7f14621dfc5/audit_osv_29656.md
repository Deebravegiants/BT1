# [C] CVE-2024-45160

## Summary
Severity: Critical
Advisory: CVE-2024-45160
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2024-10-09
Source: https://osv.dev/vulnerability/CVE-2024-45160
Type: osv

## Details
Incorrect credential validation in LemonLDAP::NG 2.18.x and 2.19.x before 2.19.2 allows attackers to bypass OAuth2 client authentication via an empty client_password parameter (client secret).

## References
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/tags
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/45xxx/CVE-2024-45160.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-45160
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/issues/3223
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/commit/06d771cbc2d5c752354c50f83e4912e5879f9aa2
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/commit/236cdfe42c1dc04a15a4a40c5e6a8c2e858d71d7
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/commit/696f49a0855faeb271096dccb8381e2129687c3d
