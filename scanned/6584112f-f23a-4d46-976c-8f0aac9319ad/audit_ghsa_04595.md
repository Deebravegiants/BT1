# [H] Hackney: `ssl:connect/2` post-handshake upgrade has no timeout

## Summary
Severity: High
Advisory: GHSA-gp9c-pm5m-5cxr
CVE: CVE-2026-47071
CWE: CWE-400
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-gp9c-pm5m-5cxr
Type: github-advisory

## Affected
- Hex: `hackney` — affected >=0.10.0 <4.0.1

## Details
### Summary

The SOCKS5 transport in `src/hackney_socks5.erl` correctly applies the caller-supplied timeout to the SOCKS5 negotiation phase, but then upgrades the tunnel to TLS using `ssl:connect/2` (the two-argument form), which defaults to `infinity`. The `Timeout` value is in scope at that call site but is never forwarded. A hostile or man-in-the-middled SOCKS5 proxy that completes the SOCKS5 handshake normally and then stalls the TLS exchange will pin the connecting Erlang process and socket indefinitely, regardless of any `connect_timeout` or `recv_timeout` options the caller set.

### Details

In `src/hackney_socks5.erl`, line 65, after the SOCKS5 negotiation succeeds, the code calls:

```erlang
ssl:connect(Socket, SSLOpts)
```

The three-argument form `ssl:connect/3` takes a timeout; the two-argument form used here defaults to `infinity`. The variable `Timeout` (already used for SOCKS5 recv calls earlier in the same function) is simply not passed. The bytes that drive the TLS handshake on the upstream side of the tunnel come from whatever endpoint the proxy connects to. A hostile proxy can complete SOCKS5 normally, then either stay silent or send a partial `ServerHello` and stop, keeping `ssl:connect/2` blocked forever. No certificate forgery is needed.

### PoC

1. Stand up a SOCKS5 proxy that completes the SOCKS5 greeting and CONNECT reply normally, then goes silent (never sends a TLS ServerHello).
2. Issue an HTTPS request through it via hackney with `connect_timeout` and `recv_timeout` set to a short value (e.g. 2000 ms).
3. Observe the calling process remains blocked well past the configured timeout, consuming a process and socket until killed externally.

### Impact

Denial of service via unbounded process and socket consumption. Affects hackney 0.10.0 through 4.0.0 for any HTTPS request routed through a SOCKS5 proxy. The `connect_timeout` and `recv_timeout` options give a false sense of safety since they are not honored during the TLS upgrade. CVSS v4.0: **8.2 (HIGH)**.

## Resources

* Introduction commit: https://github.com/benoitc/hackney/commit/34cdbd1d20a282aacc286a89327465a3925b4c5d
* Patch commit: https://github.com/benoitc/hackney/commit/5ccdab725c561a6f03d05a51f2d0664f98236dae

## References
- https://github.com/benoitc/hackney/security/advisories/GHSA-gp9c-pm5m-5cxr
- https://nvd.nist.gov/vuln/detail/CVE-2026-47071
- https://github.com/benoitc/hackney/commit/5ccdab725c561a6f03d05a51f2d0664f98236dae
- https://cna.erlef.org/cves/CVE-2026-47071.html
- https://github.com/benoitc/hackney
- https://osv.dev/vulnerability/EEF-CVE-2026-47071
