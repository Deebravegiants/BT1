# [M] CVE-2020-27607

## Summary
Severity: Medium
Advisory: CVE-2020-27607
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2020-10-21
Source: https://osv.dev/vulnerability/CVE-2020-27607
Type: osv

## Details
In BigBlueButton before 2.2.28 (or earlier), the client-side Mute button only signifies that the server should stop accepting audio data from the client. It does not directly configure the client to stop sending audio data to the server, and thus a modified server could store the audio data and/or transmit it to one or more meeting participants or other third parties.

## References
- https://www.golem.de/news/big-blue-button-das-grosse-blaue-sicherheitsrisiko-2010-151610.html
