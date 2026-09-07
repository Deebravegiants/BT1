# [H] CoreDNS has TSIG authentication bypass on gRPC and QUIC transports

## Summary
Severity: High
Advisory: GHSA-vp29-5652-4fw9
CVE: CVE-2026-35579
CWE: CWE-287
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-vp29-5652-4fw9
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0 <1.14.3

## Details
### Summary

The gRPC, QUIC, DoH, and DoH3 transports in CoreDNS incorrectly handle TSIG authentication.

For gRPC and QUIC, CoreDNS checks whether the TSIG key name exists in the config, but does not actually verify the TSIG HMAC. If the key name matches, `tsigStatus` remains nil and the tsig plugin treats the request as "verified".

For DoH and DoH3, the issue is worse: TSIG is not verified at all. The DoH response writer has `TsigStatus()` hardcoded to return nil, so any request containing a TSIG record is treated as authenticated, even if the key name is invalid and the MAC is garbage.

As a result, attackers may bypass TSIG authentication on affected transports and access TSIG-protected functionality such as AXFR/IXFR zone transfers, dynamic updates, or other TSIG-gated plugin behavior.

### Details

In `server_grpc.go` and `server_quic.go`, the TSIG handling checks whether the TSIG key name exists, but does not call `dns.TsigVerify()`.

Relevant code before fix:

```go
if tsig := msg.IsTsig(); tsig != nil {
    if s.tsigSecret == nil {
        w.tsigStatus = dns.ErrSecret
    } else if _, ok := s.tsigSecret[tsig.Hdr.Name]; !ok {
        w.tsigStatus = dns.ErrSecret
    }
    // key found -> nothing happens -> tsigStatus stays nil -> "verified"
}
```

This means that for gRPC and QUIC, a request with a known TSIG key name but an invalid MAC is accepted as authenticated.

PRs #7943 and #7947 partially addressed this area by adding key name checks for gRPC and QUIC, but did not add HMAC verification.

The DoH and DoH3 paths have an even weaker failure mode. In `https.go`, `DoHWriter.TsigStatus()` returned nil unconditionally:

```go
func (d *DoHWriter) TsigStatus() error {
    return nil
}
```

In `server_https.go`, the incoming DNS message is unpacked from the HTTP request and passed directly into `ServeDNS()` without checking `msg.IsTsig()`, without looking up the TSIG key name, and without calling `dns.TsigVerify()`.

The same pattern exists in the DoH3 path in `server_https3.go`.

The effective DoH/DoH3 flow before the fix was:

1. HTTP or HTTP/3 request arrives.
2. DNS message is unpacked from the request.
3. A `DoHWriter` is created.
4. The message is passed to `ServeDNS()`.
5. The tsig plugin checks `w.TsigStatus()`.
6. `TsigStatus()` returns nil.
7. nil is interpreted as successful TSIG verification.

This means that for DoH and DoH3, CoreDNS did not even require a valid TSIG key name. Any TSIG record was enough to satisfy the tsig plugin, regardless of key name or MAC contents.

### PoC

Setup: built CoreDNS from master at commit `12d9457` and also verified against the v1.14.2 release binary. Configured a single test zone with 9 records and `tsig { require all }`.

Listeners used the same TSIG configuration and key:

- TCP on port 1053, using the normal `dns.Server` path where TSIG HMAC verification works correctly
- gRPC on port 1443, using manual TSIG handling
- DoH on port 8443
- DoH3 with the same TSIG configuration

#### gRPC / QUIC behavior

A test client sent AXFR requests over gRPC with a valid TSIG key name but forged MAC values. The same requests were sent over TCP for comparison.

| MAC used | gRPC | TCP |
|----------|------|-----|
| 32 zero bytes | BYPASS, 9 records returned | BADSIG |
| 32 random bytes | BYPASS, 9 records returned | BADSIG |
| HMAC computed with wrong secret | BYPASS, 9 records returned | BADSIG |
| truncated to 16 bytes | BYPASS, 9 records returned | BADSIG |
| single byte `0x41` | BYPASS, 9 records returned | BADSIG |
| empty MAC | BYPASS, 9 records returned | BADSIG |
| wrong key name + zero MAC | REJECTED, NOTAUTH/BADKEY | REJECTED, NOTAUTH/BADKEY |

6 out of 7 forged TSIG requests bypassed authentication over gRPC and returned a full zone transfer. The only rejected case was the wrong key name, because the gRPC path checked whether the key name existed.

The same class applied to QUIC.

#### DoH / DoH3 behavior

For DoH, a test client sent DNS queries over HTTPS POST to `/dns-query` with forged TSIG records. These requests were also compared against TCP.

| TSIG variant | DoH result | TCP result |
|-------------|------------|------------|
| 32 zero bytes | BYPASS, NOERROR | BADSIG |
| 32 random bytes | BYPASS, NOERROR | BADSIG |
| HMAC computed with wrong secret | BYPASS, NOERROR | BADSIG |
| truncated to 16 bytes | BYPASS, NOERROR | BADSIG |
| single byte `0x41` | BYPASS, NOERROR | BADSIG |
| empty MAC | BYPASS, NOERROR | BADSIG |
| bad key name | BYPASS, NOERROR | NOTAUTH/BADKEY |
| no TSIG record | REJECTED, REFUSED | REJECTED, REFUSED |

7 out of 8 cases bypassed authentication over DoH. Every request containing a TSIG record was accepted, including requests with an invalid key name.

An AXFR request over DoH with a forged TSIG record using a zero-byte MAC returned the full test zone.

The same pattern applies to DoH3 because it used the same `DoHWriter` TSIG behavior and did not verify TSIG before passing the message into the plugin chain.

To confirm that the tsig plugin itself was enforcing policy, requests with no TSIG record were rejected with `REFUSED`. The bypass happens because the transport layer reports successful TSIG verification when verification either did not happen or only checked the key name.

### Impact

An unauthenticated network attacker may bypass TSIG authentication on affected CoreDNS transports.

Depending on configuration, this may allow an attacker to:

- perform AXFR or IXFR zone transfers over affected transports
- dump TSIG-protected zone data
- submit dynamic DNS updates if enabled
- bypass other TSIG-gated plugin behavior
- authenticate over DoH or DoH3 without knowing a valid TSIG key name

The DoH and DoH3 variants have a lower exploitation bar than gRPC and QUIC because the attacker does not need to know a configured TSIG key name. Any TSIG record is treated as valid.

### Affected transports

- gRPC
- QUIC
- DoH
- DoH3

### Workarounds

If upgrading is not immediately possible:

- Disable gRPC, QUIC, DoH, and DoH3 listeners where TSIG authentication is required.
- Restrict network-level access to affected transport ports to trusted sources only.
- Avoid exposing TSIG-protected functionality such as AXFR, IXFR, or dynamic updates over affected transports.

### Fix

Affected transports must verify TSIG before passing the DNS message into the plugin chain.

For requests containing a TSIG record, the transport should:

1. check whether TSIG secrets are configured
2. verify that the TSIG key name exists
3. call `dns.TsigVerify()` against the original wire-format message
4. store the resulting status in the response writer
5. return that status from `TsigStatus()`

A successful key name lookup alone is not sufficient. A nil TSIG status must only be returned after successful HMAC verification.

## References
- https://github.com/coredns/coredns/security/advisories/GHSA-vp29-5652-4fw9
- https://nvd.nist.gov/vuln/detail/CVE-2026-35579
- https://github.com/coredns/coredns
- https://github.com/coredns/coredns/releases/tag/v1.14.3
