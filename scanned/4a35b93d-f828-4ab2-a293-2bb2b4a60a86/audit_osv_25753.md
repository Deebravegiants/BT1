# [H] Non-MFA account takeover via using only SSH public key to login in jumpserver

## Summary
Severity: High
Advisory: CVE-2023-43652
Aliases: GHSA-fr8h-xh5x-r8g9
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2023-09-27
Source: https://osv.dev/vulnerability/CVE-2023-43652
Type: osv

## Details
JumpServer is an open source bastion host. As an unauthenticated user, it is possible to authenticate to the core API with a username and an SSH public key without needing a password or the corresponding SSH private key. An SSH public key should be considered public knowledge and should not used as an authentication secret alone. JumpServer provides an API for the KoKo component to validate user private key logins. This API does not verify the source of requests and will generate a personal authentication token. Given that public keys can be easily leaked, an attacker can exploit the leaked public key and username to authenticate, subsequently gaining access to the current user's information and authorized actions. This issue has been addressed in versions 2.28.20 and 3.7.1. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/43xxx/CVE-2023-43652.json
- https://github.com/jumpserver/jumpserver/security/advisories/GHSA-fr8h-xh5x-r8g9
- https://nvd.nist.gov/vuln/detail/CVE-2023-43652
- https://www.sonarsource.com/blog/diving-into-jumpserver-attackers-gateway-to-internal-networks-1-2
