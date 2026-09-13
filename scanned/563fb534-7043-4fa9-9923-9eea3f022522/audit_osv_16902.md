# [C] CVE-2020-10595

## Summary
Severity: Critical
Advisory: CVE-2020-10595
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-03-31
Source: https://osv.dev/vulnerability/CVE-2020-10595
Type: osv

## Details
pam-krb5 before 4.9 has a buffer overflow that might cause remote code execution in situations involving supplemental prompting by a Kerberos library. It may overflow a buffer provided by the underlying Kerberos library by a single '\0' byte if an attacker responds to a prompt with an answer of a carefully chosen length. The effect may range from heap corruption to stack corruption depending on the structure of the underlying Kerberos library, with unknown effects but possibly including code execution. This code path is not used for normal authentication, but only when the Kerberos library does supplemental prompting, such as with PKINIT or when using the non-standard no_prompt PAM configuration option.

## References
- https://usn.ubuntu.com/4314-1/
- https://www.eyrie.org/~eagle/software/pam-krb5/security/2020-03-30.html
- https://lists.debian.org/debian-lts-announce/2020/04/msg00000.html
- https://www.debian.org/security/2020/dsa-4648
- http://www.openwall.com/lists/oss-security/2020/03/31/1
- https://github.com/rra/pam-krb5/commit/e7879e27a37119fad4faf133a9f70bdcdc75d760
