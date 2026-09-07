# [M] Taskcluster web-server OAuth2 authorization codes are reusable and the exchange handler checks the wrong expiry column

## Summary
Severity: Medium
Program: Mozilla
Weakness: Authentication Bypass by Capture-replay
Reporter: anshuman_bh
State: resolved
Disclosed: 2026-06-23T12:37:52.822Z
Source: https://hackerone.com/reports/3734676

## Details
The Taskcluster web-server's OAuth2 token-exchange handler does not consume authorization codes and does not enforce the authorization-code expiry. A leaked authorization code can be replayed to mint additional bridge access tokens for the original user, well past the 10-minute window that RFC 6749 §4.1.2 requires.

# Source-to-sink

Two bugs in `services/web-server/src/servers/oauth2.js`, both in the same handler at lines 165-199:

1. The exchange handler validates `redirect_uri` and code existence, mints a bridge access token, and returns — it never deletes or otherwise consumes the `authorization_codes` row. RFC 6749 §4.1.2 requires single-use codes: "The client MUST NOT use the authorization code more than once. If an authorization code is used more than once, the authorization server MUST deny the request..."

2. The expiry check at line 66 reads `entry.client_details.expires`, which is the requested lifetime of the resulting Taskcluster credentials (capped by the registered OAuth client's `maxExpires`, e.g. `"1 year"` in the test config). The authorization-code row's intended 10-minute lifetime (`entry.expires`, set at line 33 to `taskcluster.fromNow('10 minutes')`) is never checked at exchange time. Expired codes remain usable until the daily `cleanup-expire-auth-codes` cron deletes them (`services/web-server/procs.yml:20-24`).

The same expiry-column mismatch repeats in the bridge-token-to-credentials handler at `oauth2.js:318-375` (`/login/oauth/credentials`), which checks `entry.client_details.expires` rather than the access-token row's `entry.expires`.

# Reproduction (end-to-end PoC)

End-to-end PoC reproduces against unmodified Taskcluster source at commit `246cb765672da1fdc1b7e6901002725bf0e50090` (default branch `main`). The test case extends the existing `services/web-server/test/third_party_test.js` and runs via the project's existing Mocha test infrastructure:

```
$ source ~/.nvm/nvm.sh && nvm use 24.15.0
$ cd taskcluster && yarn install
$ docker compose up -d postgres
$ docker exec taskcluster-postgres-1 psql -U postgres -c "CREATE DATABASE \"taskcluster-test\";"
$ cd services/web-server
$ TEST_DB_URL=postgresql://postgres@localhost:5432/taskcluster-test NODE_ENV=test \
    yarn mocha --grep "TC-002" test/third_party_test.js
```

Result:

```
services/web-server/test/third_party_test.js
  unit
    ✔ TC-002 (PoC): authorization code is reusable in violation of RFC 6749 §4.1.2

1 passing
```

The test:


_Trimmed to 38 lines — full report: https://hackerone.com/reports/3734676_
