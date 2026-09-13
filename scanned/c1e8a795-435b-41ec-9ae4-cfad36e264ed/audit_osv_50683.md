# [H] CVE-2020-28086

## Summary
Severity: High
Advisory: CVE-2020-28086
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2020-12-09
Source: https://osv.dev/vulnerability/CVE-2020-28086
Type: osv

## Details
pass through 1.7.3 has a possibility of using a password for an unintended resource. For exploitation to occur, the user must do a git pull, decrypt a password, and log into a remote service with the password. If an attacker controls the central Git server or one of the other members' machines, and also controls one of the services already in the password store, they can rename one of the password files in the Git repository to something else: pass doesn't correctly verify that the content of a file matches the filename, so a user might be tricked into decrypting the wrong password and sending that to a service that the attacker controls. NOTE: for environments in which this threat model is of concern, signing commits can be a solution.

## References
- https://lists.zx2c4.com/pipermail/password-store/2014-March/000498.html
