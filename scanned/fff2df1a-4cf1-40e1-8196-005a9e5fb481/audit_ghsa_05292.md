# [M] AdGuard Home: DoQ-to-UDP State Reduction and Source-Port Oracle

## Summary
Severity: Medium
Advisory: GHSA-xgx4-4h9w-53pv
CVE: CVE-2026-47703
CWE: CWE-330, CWE-362, CWE-662
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-xgx4-4h9w-53pv
Type: github-advisory

## Affected
- Go: `github.com/AdguardTeam/AdGuardHome` — affected >=0 <0.107.75
- Go: `github.com/AdguardTeam/dnsproxy` — affected >=0 <0.81.3

## Details
## Summary

This report covers the client-triggered DoQ forwarding path in:

- `dnsproxy` `v0.81.2` (`adguard/dnsproxy:v0.81.2`)
- `AdGuard Home` `v0.107.74` (`adguard/adguardhome:latest`, image version label `v0.107.74`)

The issue was reproduced on `2026-04-25` with the products configured through
their documented DoQ listener and plain UDP upstream surfaces. The scope is the
internal backend UDP hop created when a DoQ query is forwarded to a `udp://`
upstream.

On that path, the backend DNS `ID` is not preserved as an independent source of
entropy. For both products, the backend observer saw `dns_id=0` for every
sampled client-triggered query on the tested path. Repeated reruns then showed
the same `txid=0` behavior and the same positive source-port oracle on every
sampled run. A separate quoted-port ICMP oracle distinguished the correct
backend UDP source port from a wrong one with a stable, client-visible behavior
change.

Attached evidence:

- `dnsproxy` oracle path on `v0.81.2`: [attachments/artifacts/g03/20260425T141500Z-g03-v0812/summary.txt](attachments/artifacts/g03/20260425T141500Z-g03-v0812/summary.txt)
- `dnsproxy` `v0.81.2` repeatability: [attachments/artifacts/g03/repeatability-v0812.md](attachments/artifacts/g03/repeatability-v0812.md)
- `dnsproxy` steering follow-up on `v0.81.2`: [attachments/artifacts/g04/20260425T141900Z-g04-v0812/summary.txt](attachments/artifacts/g04/20260425T141900Z-g04-v0812/summary.txt)
- `AdGuard Home` oracle path: [attachments/artifacts/g05/20260425T113000Z-g05/summary.txt](attachments/artifacts/g05/20260425T113000Z-g05/summary.txt)

## Root Cause Analysis

The observable behavior is consistent across both products:

1. A DoQ client query is accepted on the frontend listener.
2. The query is forwarded over a backend UDP leg.
3. On that backend leg, the forwarded DNS `ID` collapses to `0` on the
   client-triggered path instead of remaining a fresh per-query variable.
4. The backend UDP source port is still allocated per query.
5. When an ICMP error quotes the actual backend source port, the forwarding path
   flips behavior in a way that does not occur for a wrong quoted port.

That combination removes `txid` from the backend tuple on the tested path and
leaves the UDP source port as the main remaining variable. In practical terms,
the backend hop stops behaving like a fresh `(txid, source-port)` pair per
forwarded query and instead becomes a one-variable state exposure.

For `dnsproxy`, the correct quoted port does more than produce a failure signal:
it can push resolution away from the primary UDP upstream and into the fallback
upstream. For `AdGuard Home`, the same condition produces a fast `SERVFAIL`.

## Reproduce

Prerequisites:

- Docker and Docker Compose
- OpenSSL
- build the lab helper image used by the attached harness and observer

The attached reproducer bundle contains only the files needed for this report:

- scripts: `attachments/scripts/`
- helper image build files: `attachments/docker/unbound-doq-attacker/`
- compose files: `attachments/docker-compose.g03.yml`,
  `attachments/docker-compose.g04.yml`, `attachments/docker-compose.g05.yml`
- shipped evidence: `attachments/artifacts/...`

Build the helper image first:

1. `cd attachments`
2. `docker build -t unbound-doq-attacker:latest -f docker/unbound-doq-attacker/Dockerfile docker/unbound-doq-attacker`

To rerun `dnsproxy`:

1. `cd attachments`
2. `bash scripts/repro-g03-dnsproxy-oracle.sh`
3. Inspect `artifacts/g03/<RUN_ID>/summary.txt`
4. Inspect `artifacts/g03/<RUN_ID>/entropy-backend.jsonl`,
   `txid_correct-backend.jsonl`, and `port_correct-backend.jsonl`

To rerun the `dnsproxy` fallback-steering case:

1. `cd attachments`
2. `bash scripts/repro-g04-dnsproxy-steering.sh`
3. Inspect `artifacts/g04/<RUN_ID>/summary.txt`
4. Inspect `steering_correct-main.jsonl` and `steering_correct-fallback.jsonl`

To rerun `AdGuard Home`:

1. `cd attachments`
2. `bash scripts/repro-g05-adguardhome-oracle.sh`
3. Inspect `artifacts/g05/<RUN_ID>/summary.txt`
4. Inspect `entropy-backend.jsonl`, `txid_correct-backend.jsonl`, and
   `port_correct-backend.jsonl`

The attached evidence includes fresh `dnsproxy v0.81.2` reruns, one official-
profile `AdGuard Home` run, and the minimal reproducer bundle used by both.

## Impact

For both products, the tested DoQ-to-UDP path is no longer a full
`(txid, source-port)` search surface:

- `dnsproxy`: four of four sampled runs showed `txid=0` on the backend hop and
  a positive source-port oracle on `v0.81.2`. The remaining unknown is
  `port_only`. Median wrong/correct port latency was `327.99 ms / 40.93 ms`.
- `AdGuard Home`: four of four sampled runs showed `txid=0` on the backend hop
  and a positive source-port oracle. The aggregate again classifies the
  remaining unknown as `port_only`. Median wrong/correct port latency was
  `319.14 ms / 37.02 ms`.

Product-specific effects:

- `dnsproxy`: a correct port guess produced an empty client-visible answer on
  the base oracle path, and in the fallback profile it steered all eight tested
  queries away from the main upstream and into the fallback upstream.
- `AdGuard Home`: a correct port guess produced fast `SERVFAIL` and an extra
  backend query.

This is the security-relevant point. On the tested official profiles, the
backend hop no longer forces an off-path attacker to deal with two fresh random
fields per forwarded DNS race. The DNS ID is already known: it is
deterministically `0` on the client-triggered DoQ-to-UDP path. The only
remaining backend tuple variable is the UDP source port, and the attached
evidence shows a repeatable oracle for that remaining variable.

That places the path in the same threat-model class as oracle-assisted DNS
forgery work such as SAD DNS and TUdoor: the attack first uses an oracle to
learn or validate the tuple state that protects an off-path response race, and
only then attempts the forged response. This report stops short of a forgery
demo, but the evidence already shows the crucial precondition on the tested
backend hop: the tuple is not high-entropy anymore. It has been reduced from
`(txid, source-port)` to `source-port` only.


---

**Attachments**
[attachments.zip](https://github.com/user-attachments/files/27227054/attachments.zip)

## References
- https://github.com/AdguardTeam/AdGuardHome/security/advisories/GHSA-xgx4-4h9w-53pv
- https://nvd.nist.gov/vuln/detail/CVE-2026-47703
- https://github.com/AdguardTeam/dnsproxy/commit/f00d992ce9567a50f596853978ad6500acfdcf1d
- https://github.com/AdguardTeam/AdGuardHome
- https://pkg.go.dev/vuln/GO-2026-5756
