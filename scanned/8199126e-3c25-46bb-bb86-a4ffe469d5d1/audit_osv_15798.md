# [C] CVE-2019-19791

## Summary
Severity: Critical
Advisory: CVE-2019-19791
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-29
Source: https://osv.dev/vulnerability/CVE-2019-19791
Type: osv

## Details
In LemonLDAP::NG (aka lemonldap-ng) before 2.0.7, the default Apache HTTP Server configuration does not properly restrict access to SOAP/REST endpoints (when some LemonLDAP::NG setup options are used). For example, an attacker can insert index.fcgi/index.fcgi into a URL to bypass a Require directive.

## References
- https://projects.ow2.org/view/lemonldap-ng/lemonldap-ng-2-0-7-is-out
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/issues/1943
