# [H] CVE-2019-5440

## Summary
Severity: High
Advisory: CVE-2019-5440
CVSS: 8.1 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-05-28
Source: https://osv.dev/vulnerability/CVE-2019-5440
Type: osv

## Details
Use of cryptographically weak PRNG in the password recovery token generation of Revive Adserver < v4.2.1 causes a potential authentication bypass attack if an attacker exploits the password recovery functionality. In lib/OA/Dal/PasswordRecovery.php, the function generateRecoveryId() generates a password reset token that relies on the PHP uniqid function and consequently depends only on the current server time, which is often visible in an HTTP Date header.

## References
- https://hackerone.com/reports/576504
