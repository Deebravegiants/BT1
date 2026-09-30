# [H] emp3r0r Affected by Concurrent Map Access DoS (panic/crash)

## Summary
Severity: High
Advisory: GHSA-f5p9-j34q-pwcc
CVE: CVE-2026-26201
CWE: CWE-362, CWE-663
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2026-02-17
Source: https://github.com/advisories/GHSA-f5p9-j34q-pwcc
Type: github-advisory

## Affected
- Go: `github.com/jm33-m0/emp3r0r/core` — affected >=0 <0.0.0-20260212232424-ea4d074f081d

## Details
## Summary

Multiple shared maps are accessed without consistent synchronization across goroutines. Under concurrent activity, Go runtime can trigger `fatal error: concurrent map read and map write`, causing C2 process crash (availability loss).

## Vulnerable Component(with code examples)

Operator relay map had mixed access patterns (iteration and mutation without a single lock policy):

```go
// vulnerable pattern (operator session map)
for sessionID, op := range OPERATORS { // iteration path
    ...
}

// concurrent mutation path elsewhere
OPERATORS[operatorSession] = &operator_t{...}
delete(OPERATORS, operatorSession)
```

Port-forwarding session map had read/write paths guarded inconsistently:

```go
// vulnerable pattern (port forward map)
if sess, ok := PortFwds[id]; ok { // read path
    ...
}

PortFwds[id] = newSession // write path
delete(PortFwds, id)      // delete path
```

FTP stream map similarly mixed concurrent iteration with mutation:

```go
// vulnerable pattern (FTP stream map)
for token, stream := range FTPStreams { // iteration path
    ...
}

FTPStreams[token] = stream // write path
delete(FTPStreams, token)  // delete path
```

## Attack Vector

1. Attacker (or stress traffic in authenticated flows) triggers high concurrency in normal control paths.
2. Operator sessions connect/disconnect while message forwarding and file-transfer workflows are active.
3. Concurrent read/write hits shared maps.
4. Go runtime panics with concurrent map read/write error.
5. C2 component exits, producing denial of service.

## Proof of Concept

1. Start C2 server with active operator session(s) in a lab environment.
2. Generate rapid operator session churn (connect/disconnect loops).
3. Simultaneously drive agent message tunnel traffic and/or file transfer activity.
4. Observe crash signature in logs: `fatal error: concurrent map read and map write`.
5. Optional: run with race detector in dev build to confirm race locations.

## Impact

- C2 service interruption due to process panic/crash.
- Operational instability under load or deliberate churn.
- Repeated crash-restart cycles can degrade command reliability and incident response workflows.

## References
- https://github.com/jm33-m0/emp3r0r/security/advisories/GHSA-f5p9-j34q-pwcc
- https://nvd.nist.gov/vuln/detail/CVE-2026-26201
- https://github.com/jm33-m0/emp3r0r/commit/ea4d074f081dac6293f3aec38f01def5f08d5af5
- https://github.com/jm33-m0/emp3r0r
- https://github.com/jm33-m0/emp3r0r/releases/tag/v3.21.2
