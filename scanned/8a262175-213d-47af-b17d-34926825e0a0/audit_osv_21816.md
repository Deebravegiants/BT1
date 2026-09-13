# [M] CVE-2021-46701

## Summary
Severity: Medium
Advisory: CVE-2021-46701
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-02-20
Source: https://osv.dev/vulnerability/CVE-2021-46701
Type: osv

## Details
PreMiD 2.2.0 allows unintended access via the websocket transport. An attacker can receive events from a socket and emit events to a socket, potentially interfering with a victim's "now playing" status on Discord.

## References
- https://github.com/PreMiD/PreMiD/issues/790
- https://github.com/PreMiD/PreMiD/pull/791
