# [M] CVE-2021-34421

## Summary
Severity: Medium
Advisory: CVE-2021-34421
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:N/A:N)
Published: 2021-11-11
Source: https://osv.dev/vulnerability/CVE-2021-34421
Type: osv

## Details
The Keybase Client for Android before version 5.8.0 and the Keybase Client for iOS before version 5.8.0 fails to properly remove exploded messages initiated by a user if the receiving user places the chat session in the background while the sending user explodes the messages. This could lead to disclosure of sensitive information which was meant to be deleted from the customer's device.

## References
- https://explore.zoom.us/en/trust/security/security-bulletin
