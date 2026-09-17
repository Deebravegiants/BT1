# [M] Remote Memory Disclosure in bittorrent-dht

## Summary
Severity: Medium
Advisory: GHSA-77g4-36jp-5v3m
CVE: CVE-2016-10519
CWE: CWE-201
Ecosystem: npm
Published: 2020-09-01
Source: https://github.com/advisories/GHSA-77g4-36jp-5v3m
Type: github-advisory

## Affected
- npm: `bittorrent-dht` — affected >=0 <5.1.3

## Details
Versions of `bittorrent-dht` prior to 5.1.3 are affected by a remote memory disclosure vulnerability. This vulnerability allows an attacker to send a specific series of of messages to a listening peer and get it to reveal internal memory.


There are two mitigating factors here, that slightly reduce the impact of this vulnerability:

1. Any modern kernel will zero out new memory pages before handing them off to a process. This means that only memory previously used and deallocated by the node process can be leaked.
1. Node.js manages Buffers by creating a few large internal SlowBuffers, and slicing them up into smaller Buffers which are made accessible in JS. They are not stored on V8's heap, because garbage collection would interfere. The result is that only memory that has been previously allocated as a Buffer can be leaked.


## Recommendation

Update to version 5.1.3 or later.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2016-10519
- https://github.com/feross/bittorrent-dht/issues/87
- https://www.npmjs.com/advisories/68
