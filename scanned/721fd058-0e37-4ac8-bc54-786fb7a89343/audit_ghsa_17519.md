# [H] Pion Interceptor's improper RTP padding handling allows remote crash for SFU users (DoS)

## Summary
Severity: High
Advisory: GHSA-f26w-gh5m-qq77
CVE: CVE-2025-49140
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-06-09
Source: https://github.com/advisories/GHSA-f26w-gh5m-qq77
Type: github-advisory

## Affected
- Go: `github.com/pion/interceptor` — affected >=0.1.36 <0.1.39

## Details
### Impact
Pion Interceptor versions v0.1.36 through v0.1.38 contain a bug in a RTP packet factory that can be exploited to trigger a panic with Pion based SFU via crafted RTP packets, This only affect users that use pion/interceptor.

### Patches

Upgrade to v0.1.39 or later, which includes PR [#338](https://github.com/pion/interceptor/pull/338) which validates that: `padLen > 0 && padLen <= payloadLength` and return error  on overflow, avoiding panic.

If upgrading is not possible, apply the patch from the pull request manually or drop packets whose P-bit is set but whose padLen is zero or larger than the remaining payload.

### Workarounds
At the application layer, reject any RTP packet where:
```
hasPadding (P-bit field) == true  &&  (padLen == 0 || padLen > packetLen – headerLen)
```

before passing it to Pion’s packet factories.

### References
Commit fixing the bug: https://github.com/pion/interceptor/commit/fa5b35ea867389cec33a9c82fffbd459ca8958e5
Pull request: https://github.com/pion/interceptor/pull/338
Issue: https://github.com/pion/webrtc/issues/3148

## References
- https://github.com/pion/interceptor/security/advisories/GHSA-f26w-gh5m-qq77
- https://nvd.nist.gov/vuln/detail/CVE-2025-49140
- https://github.com/pion/webrtc/issues/3148
- https://github.com/pion/interceptor/pull/338
- https://github.com/pion/interceptor/commit/fa5b35ea867389cec33a9c82fffbd459ca8958e5
- https://github.com/pion/interceptor
