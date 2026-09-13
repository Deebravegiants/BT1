# [C] CVE-2023-28862

## Summary
Severity: Critical
Advisory: CVE-2023-28862
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-03-31
Source: https://osv.dev/vulnerability/CVE-2023-28862
Type: osv

## Details
An issue was discovered in LemonLDAP::NG before 2.16.1. Weak session ID generation in the AuthBasic handler and incorrect failure handling during a password check allow attackers to bypass 2FA verification. Any plugin that tries to deny session creation after the store step does not deny an AuthBasic session.

## References
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/releases/v2.16.1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/28xxx/CVE-2023-28862.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-28862
- https://gitlab.ow2.org/lemonldap-ng/lemonldap-ng/-/issues/2896
- https://lists.debian.org/debian-lts-announce/2023/07/msg00018.html
