# [H] Improper session handling of "Remember me for 7 days" functionality

## Summary
Severity: High
Advisory: CVE-2023-23614
Aliases: GHSA-33w4-xf7m-f82m
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-01-26
Source: https://osv.dev/vulnerability/CVE-2023-23614
Type: osv

## Details
Pi-hole®'s Web interface (based off of AdminLTE) provides a central location to manage your Pi-hole. Versions 4.0 and above, prior to 5.18.3 are vulnerable to Insufficient Session Expiration. Improper use of admin WEBPASSWORD hash as "Remember me for 7 days" cookie value makes it possible for an attacker to "pass the hash" to login or reuse a theoretically expired "remember me" cookie. It also exposes the hash over the network and stores it unnecessarily in the browser. The cookie itself is set to expire after 7 days but its value will remain valid as long as the admin password doesn't change. If a cookie is leaked or compromised it could be used forever as long as the admin password is not changed. An attacker that obtained the password hash via an other attack vector (for example a path traversal vulnerability) could use it to login as the admin by setting the hash as the cookie value without the need to crack it to obtain the admin password (pass the hash). The hash is exposed over the network and in the browser where the cookie is transmitted and stored. This issue is patched in version 5.18.3.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23614.json
- https://github.com/pi-hole/AdminLTE/security/advisories/GHSA-33w4-xf7m-f82m
- https://nvd.nist.gov/vuln/detail/CVE-2023-23614
