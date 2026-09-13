# [H] CVE-2019-3560

## Summary
Severity: High
Advisory: CVE-2019-3560
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-04-29
Source: https://osv.dev/vulnerability/CVE-2019-3560
Type: osv

## Details
An improperly performed length calculation on a buffer in PlaintextRecordLayer could lead to an infinite loop and denial-of-service based on user input. This issue affected versions of fizz prior to v2019.03.04.00.

## References
- http://packetstormsecurity.com/files/172836/polkit-Authentication-Bypass.html
- http://packetstormsecurity.com/files/172846/Facebook-Fizz-Denial-Of-Service.html
- https://github.com/facebookincubator/fizz/commit/40bbb161e72fb609608d53b9d64c56bb961a6ee2
