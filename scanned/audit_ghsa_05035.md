# [H] python-engineio has possible denial of service due to maximum payload size sometimes not being enforced

## Summary
Severity: High
Advisory: GHSA-m9gh-vj53-gvh9
CVE: CVE-2026-48809
CWE: CWE-770
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-m9gh-vj53-gvh9
Type: github-advisory

## Affected
- PyPI: `python-engineio` — affected >=0 <4.13.2

## Details
### Impact
There are two specific configurations of the python-engineio server in which the size of incoming messages is not checked before the messages are loaded into memory. An attacker can take advantage of these to cause unnecessary memory allocations in the python-engineio server. The two cases are:

- POST requests, when using ASGI with the long polling transport
- WebSocket messages, when using Aiohttp with the WebSocket transport

### Patches
Version 4.13.2 addresses this issue as follows:

- ASGI severs now only load the body of incoming requests into memory after the client is confirmed to be known and authenticated, and the payload size is below the maximum allowed size. Requests that do not comply with these requirements are discarded.
- Aiohttp servers configure the maximum payload size in the underlying WebSocket layer from Aiohttp, so that large messages are discarded by Aiohttp before they are delivered to python-engineio.

## References
- https://github.com/miguelgrinberg/python-engineio/security/advisories/GHSA-m9gh-vj53-gvh9
- https://github.com/miguelgrinberg/python-engineio
