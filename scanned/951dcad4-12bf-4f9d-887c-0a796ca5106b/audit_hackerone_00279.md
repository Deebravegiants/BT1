# [H] CVE-2017-8798 - miniupnp getHTTPResponse chunked encoding integer signedness error

## Summary
Severity: High (CVSS 7.1)
Program: Internet Bug Bounty
Weakness: Integer Overflow
Reporter: hxd
State: resolved
Disclosed: 2019-11-12T23:48:49.780Z
CVE: CVE-2017-8798
Source: https://hackerone.com/reports/227344

## Details
### Integer signedness error in miniupnpc [1]  allows remote attackers to cause a denial of service condition (access violation and heap corruption) via specially crafted HTTP response

An integer signedness error was found in miniupnp's `miniwget` allowing 
an unauthenticated remote entity typically located on the
local network segment to trigger a heap corruption or an access violation
in miniupnp's http response parser when processing a specially crafted
chunked-encoded response to a request for the xml root description url.

* affects
 * all versions >= `v1.4.20101221` (released 21/12/2010; `~6 years ago`)
 * all configurations as its a core part of the library
* impact
 * DoS (access violation due to buffer overread memcpy)
 * Heap Overwrite (pot. race RCE in multithreaded envs)
* requirements
  * no user interaction, unauth, low complexity
* how widespread is this software?
 * miniupnpc is compiled into a wide range of network applications and embedded device firmware.
 * blockchain clients: `bitcoind` and almost all forks, `CPP ethereum`, ...
 * p2p filesharing applications: `qBittorrent`, `Transmission`, ...
 * network device firmware: `dlink`, `linksys`, probably `synology` or anything that allows IGD management / portforwarding
 * numerous hits for `miniwget` on google or github.  closed source obviously not included but its likely to find this lib packed with embedded devices.
* disclosure
 * provided detailed description, PoC and patch
 * status: fixed; within 8 days.

The vulnerable component is a HTTP file download method called 
`miniwget` (precisely `getHTTPResponse`) that fails to properly handle 
invalid chunked-encoded HTTP responses. The root cause is a bounds check
that mistakenly casts an unsigned attacker-provided chunksize to signed 
int leading to an incorrect decision on the destination heap buffer size 
when copying data from the server response to an internal buffer. The 
attacker controls both the size of the internal buffer as well as the 
number of bytes to copy. In order for this attack to succeed, the number 
of bytes to copy must be negative.

attacker controls:
* `int content_length`

_Trimmed to 38 lines — full report: https://hackerone.com/reports/227344_
