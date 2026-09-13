# [H] CVE-2018-9275

## Summary
Severity: High
Advisory: CVE-2018-9275
CVSS: 8.2 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:H)
Published: 2018-04-04
Source: https://osv.dev/vulnerability/CVE-2018-9275
Type: osv

## Details
In check_user_token in util.c in the Yubico PAM module (aka pam_yubico) 2.18 through 2.25, successful logins can leak file descriptors to the auth mapping file, which can lead to information disclosure (serial number of a device) and/or DoS (reaching the maximum number of file descriptors).

## References
- https://bugzilla.opensuse.org/show_bug.cgi?id=1088027
- https://github.com/Yubico/yubico-pam/issues/136
- https://github.com/Yubico/yubico-pam/commit/0f6ceabab0a8849b47f67d727aa526c2656089ba
