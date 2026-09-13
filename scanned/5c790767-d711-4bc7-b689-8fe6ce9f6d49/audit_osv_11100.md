# [H] CVE-2017-6062

## Summary
Severity: High
Advisory: CVE-2017-6062
CVSS: 8.6 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:H/A:N)
Published: 2017-03-02
Source: https://osv.dev/vulnerability/CVE-2017-6062
Type: osv

## Details
The "OpenID Connect Relying Party and OAuth 2.0 Resource Server" (aka mod_auth_openidc) module before 2.1.5 for the Apache HTTP Server does not skip OIDC_CLAIM_ and OIDCAuthNHeader headers in an "OIDCUnAuthAction pass" configuration, which allows remote attackers to bypass authentication via crafted HTTP traffic.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2V3HIGXMUKJGOBMAQAQPGC7G5YYWSUVA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EJXBG3DG2FUYFGTUTSJFMPIINVFKKB4Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WTWUMQ46GZY3O4WU4JCF333LN53R2XQH/
- https://github.com/pingidentity/mod_auth_openidc/blob/master/ChangeLog
- https://github.com/pingidentity/mod_auth_openidc/issues/222
- https://github.com/pingidentity/mod_auth_openidc/releases/tag/v2.1.5
