# [H] Manipulation of Internal Dovecot Variables in mailcow via crafted Passwords

## Summary
Severity: High
Advisory: CVE-2023-34108
Aliases: GHSA-mhh4-qchc-pv22
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-06-07
Source: https://osv.dev/vulnerability/CVE-2023-34108
Type: osv

## Details
mailcow is a mail server suite based on Dovecot, Postfix and other open source software, that provides a modern web UI for user/server administration. A vulnerability has been discovered in mailcow which allows an attacker to manipulate internal Dovecot variables by using specially crafted passwords during the authentication process. The issue arises from the behavior of the `passwd-verify.lua` script, which is responsible for verifying user passwords during login attempts. Upon a successful login, the script returns a response in the format of "password=<valid-password>", indicating the successful authentication. By crafting a password with additional key-value pairs appended to it, an attacker can manipulate the returned string and influence the internal behavior of Dovecot. For example, using the password "123 mail_crypt_save_version=0" would cause the `passwd-verify.lua` script to return the string "password=123 mail_crypt_save_version=0". Consequently, Dovecot will interpret this string and set the internal variables accordingly, leading to unintended consequences. This vulnerability can be exploited by an authenticated attacker who has the ability to set their own password. Successful exploitation of this vulnerability could result in unauthorized access to user accounts, bypassing security controls, or other malicious activities. This issue has been patched in version `2023-05a`. Users are advised to upgrade. There are no known workarounds for this vulnerability.

## References
- https://github.com/VladimirBorisov/CVE_proposal/blob/main/MailcowUserPassword.md
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/34xxx/CVE-2023-34108.json
- https://github.com/mailcow/mailcow-dockerized/security/advisories/GHSA-mhh4-qchc-pv22
- https://nvd.nist.gov/vuln/detail/CVE-2023-34108
- https://github.com/mailcow/mailcow-dockerized/commit/f80940efdccd393bf5fccec2886795372a38c445
