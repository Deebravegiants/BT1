# [H] python-engineio has unbound thread allocation that can cause denial of service

## Summary
Severity: High
Advisory: GHSA-cgwc-pv48-fhj5
CVE: CVE-2026-48802
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-cgwc-pv48-fhj5
Type: github-advisory

## Affected
- PyPI: `python-engineio` — affected >=0 <4.13.2

## Details
### Impact
An attacker can cause the creation of unnecessary background threads in the python-engineio server by exploiting the heartbeat mechanism, which launches a thread when a new connection is received, and when the client sends a PONG packet.

Note: this issue primarily affects synchronous servers. Asynchronous servers allocate background tasks instead of physical threads, which are lightweight and less likely to cause denial of service. However, the fix that was implemented was also applied to the asynchronous case.

### Patches
Version 4.13.2 addresses this issue as follows:

- The initial background thread (or async task( for heartbeat management is only launched if a client passes authentication in the `connect` handler.
- The server now ensures that there is only one background heatbeat thread (or async task) per client at a given point in time. Out of sequence PONG packets are now discarded when an active heartbeat thread is already running.

## References
- https://github.com/miguelgrinberg/python-engineio/security/advisories/GHSA-cgwc-pv48-fhj5
- https://github.com/miguelgrinberg/python-engineio
