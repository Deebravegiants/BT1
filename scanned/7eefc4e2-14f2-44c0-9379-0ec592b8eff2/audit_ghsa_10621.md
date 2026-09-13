# [M] Rack's multipart byte range processing allows denial of service via excessive overlapping ranges

## Summary
Severity: Medium
Advisory: GHSA-x8cg-fq8g-mxfx
CVE: CVE-2026-34826
CWE: CWE-400, CWE-770
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-04-02
Source: https://github.com/advisories/GHSA-x8cg-fq8g-mxfx
Type: github-advisory

## Affected
- RubyGems: `rack` — affected >=0 <2.2.23
- RubyGems: `rack` — affected >=3.0.0.beta1 <3.1.21
- RubyGems: `rack` — affected >=3.2.0 <3.2.6

## Details
## Summary

`Rack::Utils.get_byte_ranges` parses the HTTP `Range` header without limiting the number of individual byte ranges. Although the existing fix for CVE-2024-26141 rejects ranges whose total byte coverage exceeds the file size, it does not restrict the count of ranges. An attacker can supply many small overlapping ranges such as `0-0,0-0,0-0,...` to trigger disproportionate CPU, memory, I/O, and bandwidth consumption per request.

This results in a denial of service condition in Rack file-serving paths that process multipart byte range responses.

## Details

`Rack::Utils.get_byte_ranges` accepts a comma-separated list of byte ranges and validates them based on their aggregate size, but does not impose a limit on how many individual ranges may be supplied.

As a result, a request such as:

```http
Range: bytes=0-0,0-0,0-0,0-0,...
```

can contain thousands of overlapping one-byte ranges while still satisfying the total-size check added for CVE-2024-26141.

When such a header is processed by Rack’s file-serving code, each range causes additional work, including multipart response generation, per-range iteration, file seek and read operations, and temporary string allocation for response size calculation and output. This allows a relatively small request header to trigger disproportionately expensive processing and a much larger multipart response.

The issue is distinct from CVE-2024-26141. That fix prevents range sets whose total byte coverage exceeds the file size, but does not prevent a large number of overlapping ranges whose summed size remains within that limit.

## Impact

Applications that expose file-serving paths with byte range support may be vulnerable to denial of service.

An unauthenticated attacker can send crafted `Range` headers containing many small overlapping ranges to consume excessive CPU time, memory, file I/O, and bandwidth. Repeated requests may reduce application availability and increase pressure on workers and garbage collection.

## Mitigation

* Update to a patched version of Rack that limits the number of accepted byte ranges.
* Reject or normalize multipart byte range requests containing excessive range counts.
* Consider disabling multipart range support where it is not required.
* Apply request filtering or header restrictions at the reverse proxy or application boundary to limit abusive `Range` headers.

## References
- https://github.com/rack/rack/security/advisories/GHSA-x8cg-fq8g-mxfx
- https://nvd.nist.gov/vuln/detail/CVE-2026-34826
- https://github.com/rack/rack
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2026-34826.yml
