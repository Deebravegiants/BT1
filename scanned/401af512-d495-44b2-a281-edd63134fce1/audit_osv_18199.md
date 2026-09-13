# [M] CVE-2020-24928

## Summary
Severity: Medium
Advisory: CVE-2020-24928
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2020-08-29
Source: https://osv.dev/vulnerability/CVE-2020-24928
Type: osv

## Details
managers/socketManager.ts in PreMiD through 2.1.3 has a locally hosted socketio web server (port 3020) open to all origins, which allows attackers to obtain sensitive Discord user information.

## References
- https://github.com/PreMiD/PreMiD/pull/501
