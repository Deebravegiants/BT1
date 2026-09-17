# [H] CVE-2017-6059

## Summary
Severity: High
Advisory: CVE-2017-6059
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-04-12
Source: https://osv.dev/vulnerability/CVE-2017-6059
Type: osv

## Details
Mod_auth_openidc.c in the Ping Identity OpenID Connect authentication module for Apache (aka mod_auth_openidc) before 2.14 allows remote attackers to spoof page content via a malicious URL provided to the user, which triggers an invalid request.

## References
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/2V3HIGXMUKJGOBMAQAQPGC7G5YYWSUVA/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/EJXBG3DG2FUYFGTUTSJFMPIINVFKKB4Z/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/WTWUMQ46GZY3O4WU4JCF333LN53R2XQH/
- http://www.openwall.com/lists/oss-security/2017/02/17/6
- http://www.securityfocus.com/bid/96299
- https://access.redhat.com/errata/RHSA-2019:2112
- https://github.com/pingidentity/mod_auth_openidc/commit/612e309bfffd6f9b8ad7cdccda3019fc0865f3b4
- https://github.com/pingidentity/mod_auth_openidc/issues/212
- https://github.com/pingidentity/mod_auth_openidc/releases/tag/v2.1.4
