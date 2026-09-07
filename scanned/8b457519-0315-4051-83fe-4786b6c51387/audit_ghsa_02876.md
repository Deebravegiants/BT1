# [M] Async-h1 request smuggling possible with long unread bodies

## Summary
Severity: Medium
Advisory: GHSA-4vr9-8cjf-vf9c
CVE: CVE-2020-26281
CWE: CWE-444
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:N/I:H/A:N (CVSS_V3)
Published: 2021-10-12
Source: https://github.com/advisories/GHSA-4vr9-8cjf-vf9c
Type: github-advisory

## Affected
- crates.io: `async-h1` — affected >=0 <2.3.0

## Details
### Impact
This vulnerability affects any webserver that uses async-h1 behind a reverse proxy, including all such Tide applications.

If the server does not read the body of a request which is longer than some buffer length, async-h1 will attempt to read a subsequent request from the body content starting at that offset into the body.

One way to exploit this vulnerability would be for an adversary to craft a request such that the body contains a request that would not be noticed by a reverse proxy, allowing it to forge forwarded/x-forwarded headers. If an application trusted the authenticity of these headers, it could be misled by the smuggled request.

Another potential concern with this vulnerability is that if a reverse proxy is sending multiple http clients' requests along the same keep-alive connection, it would be possible for the smuggled request to specify a long content and capture another user's request in its body. This content could be captured in a post request to an endpoint that allows the content to be subsequently retrieved by the adversary.


### Patches
This has been addressed in async-h1 2.3.0 and previous versions have been yanked.

### Workarounds
none

### References
https://github.com/http-rs/async-h1/releases/tag/v2.3.0

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [async-h1](https://github.com/http-rs/async-h1)
* Contact a core team member on [zulip](https://http-rs.zulip-chat.com) or [discord](https://discord.gg/x2gKzst)

## References
- https://github.com/http-rs/async-h1/security/advisories/GHSA-4vr9-8cjf-vf9c
- https://nvd.nist.gov/vuln/detail/CVE-2020-26281
- https://github.com/http-rs/async-h1
- https://github.com/http-rs/async-h1/releases/tag/v2.3.0
- https://rustsec.org/advisories/RUSTSEC-2020-0093.html
