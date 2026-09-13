# [H] Noise vulnerable to denial of service

## Summary
Severity: High
Advisory: GHSA-6cr6-fmvc-vw2p
CVE: CVE-2021-4239
CWE: CWE-311
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2022-12-28
Source: https://github.com/advisories/GHSA-6cr6-fmvc-vw2p
Type: github-advisory

## Affected
- Go: `github.com/flynn/noise` — affected >=0 <1.0.0

## Details
Noise is a Go implementation of the Noise Protocol Framework. The Noise protocol implementation suffers from weakened cryptographic security after encrypting 2^64 messages, and a potential denial of service attack. After 2^64 (~18.4 quintillion) messages are encrypted with the Encrypt function, the nonce counter will wrap around, causing multiple messages to be encrypted with the same key and nonce. In a separate issue, the Decrypt function increments the nonce state even when it fails to decrypt a message. If an attacker can provide an invalid input to the Decrypt function, this will cause the nonce state to desynchronize between the peers, resulting in a failure to encrypt all subsequent messages.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4239
- https://github.com/flynn/noise/pull/44
- https://github.com/flynn/noise/commit/2499bf1bad239a8316c32932a993642350b3afdb
- https://github.com/flynn/noise
- https://pkg.go.dev/vuln/GO-2022-0425
