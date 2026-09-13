# [C] CVE-2019-15941

## Summary
Severity: Critical
Advisory: CVE-2019-15941
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-09-25
Source: https://osv.dev/vulnerability/CVE-2019-15941
Type: osv

## Details
OpenID Connect Issuer in LemonLDAP::NG 2.x through 2.0.5 may allow an attacker to bypass access control rules via a crafted OpenID Connect authorization request. To be vulnerable, there must exist an OIDC Relaying party within the LemonLDAP configuration with weaker access control rules than the target RP, and no filtering on redirection URIs.

## References
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/issues/1881
- https://projects.ow2.org/view/lemonldap-ng/lemonldap-ng-2-0-6-is-out/
- https://seclists.org/bugtraq/2019/Sep/46
- https://www.debian.org/security/2019/dsa-4533
