# [C] CVE-2018-16988

## Summary
Severity: Critical
Advisory: CVE-2018-16988
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-02
Source: https://osv.dev/vulnerability/CVE-2018-16988
Type: osv

## Details
An issue was discovered in Open XDMoD through 7.5.0. An authentication bypass (account takeover) exists due to a weak password reset mechanism. A brute-force attack against an MD5 rid value requires only 600 guesses in the plausible situation where the attacker knows that the victim has started a password-reset process (pass_reset.php, password_reset.php, XDUser.php) in the past few minutes.

## References
- https://github.com/grymer/CVE/blob/master/CVE-2018-16988.md
