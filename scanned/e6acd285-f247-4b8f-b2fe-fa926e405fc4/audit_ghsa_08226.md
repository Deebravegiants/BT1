# [C] praisonai-platform: JWT signing key defaults to hardcoded "dev-secret-change-me", allowing token forgery for any user when PLATFORM_ENV is unset

## Summary
Severity: Critical
Advisory: GHSA-3qg8-5g3r-79v5
CVE: CVE-2026-47410
CWE: CWE-321, CWE-798
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-3qg8-5g3r-79v5
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.4

## Details
## Summary

**Type:** Insecure default cryptographic key. The JWT signing secret defaults to the hardcoded literal `"dev-secret-change-me"` when `PLATFORM_JWT_SECRET` is unset. A safety check exists but only fires when `PLATFORM_ENV != "dev"`; the default value of `PLATFORM_ENV` is `"dev"`, so the check is silently bypassed in any deployment that does not explicitly opt out. The attacker reads the literal from this public source file, mints a JWT with arbitrary `sub` and `email` claims, and authenticates as any existing user (including workspace owners and admins).
**File:** `src/praisonai-platform/praisonai_platform/services/auth_service.py`, lines 25-36 and 114-137.
**Root cause:** the production-mode guard checks `os.environ.get("PLATFORM_ENV", "dev") != "dev"` — but the default is `"dev"`, so a clean deployment that just imports the package and runs `uvicorn praisonai_platform.api.app:app` proceeds with the hardcoded secret. The package documentation does not warn loudly enough that BOTH variables must be set; the guard suppresses itself when either condition is missed. JWT verification at line 129 trusts whatever the token says (`sub`, `email`, `name`) once the HMAC-SHA256 signature validates against the publicly-known secret. Since the verifier accepts forged tokens for any user_id, the attacker becomes that user across every authenticated route.

## Affected Code

**File:** `src/praisonai-platform/praisonai_platform/services/auth_service.py`, lines 25-36 and 114-137.

```python
_DEFAULT_SECRET = "dev-secret-change-me"
JWT_SECRET = os.environ.get("PLATFORM_JWT_SECRET", _DEFAULT_SECRET)            # <-- BUG: silent fallback
JWT_ALGORITHM = "HS256"
JWT_TTL_SECONDS = int(os.environ.get("PLATFORM_JWT_TTL", str(30 * 24 * 3600)))

if JWT_SECRET == _DEFAULT_SECRET and os.environ.get("PLATFORM_ENV", "dev") != "dev":
    raise RuntimeError(                                                          # <-- only fires if PLATFORM_ENV is non-default
        "PLATFORM_JWT_SECRET must be set to a strong random value in production. "
        "Set PLATFORM_ENV=dev to suppress this check during development."
    )

# ...

def _issue_token(self, user: User) -> str:
    payload = {
        "sub": user.id,
        "email": user.email,
        "name": user.name,
        "iat": now,
        "exp": now + timedelta(seconds=JWT_TTL_SECONDS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)             # signs with the hardcoded secret

def _verify_token(self, token: str) -> Optional[AuthIdentity]:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])     # verifies with the hardcoded secret
        return AuthIdentity(
            id=payload["sub"],                                                  # <-- attacker chooses sub
            type="user",
            email=payload.get("email"),
            name=payload.get("name"),
        )
    except jwt.InvalidTokenError:
        return None
```

**Why it's wrong:** the guard's predicate is wrong. The intent — "warn loudly if a production deployment ships without setting the secret" — is correct, but the implementation requires the operator to set BOTH variables (`PLATFORM_JWT_SECRET` and `PLATFORM_ENV != "dev"`) for the guard to fire. A common deployment misconfiguration is to set only one (or neither): `pip install praisonai-platform`, `uvicorn praisonai_platform.api.app:app --host 0.0.0.0`, done. The package starts with no warning, the JWT signing key is the literal string sitting in this source file, and any attacker who reads the GitHub repo can forge tokens. The standard pattern is to fail-closed at import time when the secret is the default, regardless of any environment variable. The code at line 32-36 inverts that: it fails-open by default and only fails-closed when the operator opts in.

## Exploit Chain

1. Attacker reads `auth_service.py:25` from the public GitHub repo (`MervinPraison/PraisonAI`) and notes `_DEFAULT_SECRET = "dev-secret-change-me"`. State: attacker holds the JWT signing key.
2. Attacker identifies a target deployment of `praisonai-platform` (Shodan search for the FastAPI route `/auth/me`, the `praisonai_platform` user-agent, or any indexed installation). Attacker registers a free account at `POST /auth/register` to confirm the deployment is live and to obtain at least one valid JWT token whose structure they can copy. State: attacker holds a live account.
3. Attacker enumerates the platform's user IDs via any of the IDOR primitives filed as separate advisories (issue `created_by`, agent `owner_id`, comment `author_id`, member list via the workspace-member-IDOR), or simply queries `/auth/me` with their own token to learn the UUID format. State: attacker has a target user UUID `T_id` (e.g. a workspace owner of any tenant).
4. Attacker forges a JWT:
   ```python
   import jwt, time
   payload = {"sub": "T_id", "email": "victim@example.com", "name": "victim",
              "iat": int(time.time()), "exp": int(time.time()) + 3600}
   token = jwt.encode(payload, "dev-secret-change-me", algorithm="HS256")
   ```
   State: attacker holds a JWT that the deployment's `_verify_token` will accept as authentic.
5. Attacker sends `GET /auth/me` with `Authorization: Bearer <forged_token>`. `_verify_token` decodes the token using `JWT_SECRET = "dev-secret-change-me"`, the HMAC matches, an `AuthIdentity(id="T_id", ...)` is returned. The route resolves the actual `User` row by `User.id == "T_id"` and returns the victim's record. State: attacker is authenticated as the victim.
6. Attacker pivots: `POST /workspaces/{id}/members` to add themselves as owner (chaining with the companion priv-esc advisory becomes redundant — the attacker is already the victim), `PATCH /workspaces/{id}` to flip settings, `DELETE /workspaces/{id}` to wipe data, or simply `GET /workspaces/{id}/issues/...` to exfiltrate everything the victim could read.
7. Final state: full account takeover for any user_id on any deployment that did not explicitly set both `PLATFORM_JWT_SECRET` and `PLATFORM_ENV=production`. No prior auth, no user interaction, no special network position required.

## Security Impact

**Severity:** sec-critical. CVSS 9.8: network attack, low complexity, no privileges, no user interaction, scope unchanged (the JWT layer is the same component the attacker pivots through), high confidentiality, high integrity, high availability (chaining with `delete_workspace` from the companion advisory).
**Attacker capability:** mint a JWT for any `user_id` on the deployment with the public secret, becoming that user across every authenticated route. No prior authentication required — the attacker only needs the package to be deployed and reachable. This is a pre-auth full account takeover.
**Preconditions:** `praisonai-platform` is deployed without explicitly setting BOTH `PLATFORM_JWT_SECRET` AND `PLATFORM_ENV=<non-dev>`. The default deployment pattern (pip install, `uvicorn ...`) hits this. The attacker needs network reachability to the API.
**Differential:** source-inspection-verified end-to-end. The asymmetry is between the documented intent of the guard (warn in production) and its actual semantics (warn only when the operator sets `PLATFORM_ENV` to a non-"dev" value). With the suggested fix below, the guard fails-closed: any deployment that did not set `PLATFORM_JWT_SECRET` raises at import time, regardless of `PLATFORM_ENV`. The forged-token attack returns `None` from `_verify_token` because the signing key the attacker used (`"dev-secret-change-me"`) no longer matches the deployment's secret.

## Suggested Fix

Fail-closed at import time when the secret is the default, irrespective of `PLATFORM_ENV`. Permit explicit dev-mode opt-in with a separate variable that is NEVER the default.

```diff
--- a/src/praisonai-platform/praisonai_platform/services/auth_service.py
+++ b/src/praisonai-platform/praisonai_platform/services/auth_service.py
@@ -23,12 +23,16 @@
 _pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

-_DEFAULT_SECRET = "dev-secret-change-me"
-JWT_SECRET = os.environ.get("PLATFORM_JWT_SECRET", _DEFAULT_SECRET)
+JWT_SECRET = os.environ.get("PLATFORM_JWT_SECRET")
 JWT_ALGORITHM = "HS256"
 JWT_TTL_SECONDS = int(os.environ.get("PLATFORM_JWT_TTL", str(30 * 24 * 3600)))

-if JWT_SECRET == _DEFAULT_SECRET and os.environ.get("PLATFORM_ENV", "dev") != "dev":
-    raise RuntimeError(
-        "PLATFORM_JWT_SECRET must be set to a strong random value in production. "
-        "Set PLATFORM_ENV=dev to suppress this check during development."
-    )
+if not JWT_SECRET:
+    if os.environ.get("PRAISONAI_PLATFORM_ALLOW_INSECURE_JWT") != "1":
+        raise RuntimeError(
+            "PLATFORM_JWT_SECRET must be set to a strong random value (min 32 bytes). "
+            "For local development, set PRAISONAI_PLATFORM_ALLOW_INSECURE_JWT=1 to "
+            "auto-generate an ephemeral random secret per process."
+        )
+    import secrets
+    JWT_SECRET = secrets.token_urlsafe(32)
+    # ephemeral; tokens issued before restart will not validate after restart
+    import warnings
+    warnings.warn("Using ephemeral JWT secret; set PLATFORM_JWT_SECRET in production")
```

The guard now fails-closed: an unset `PLATFORM_JWT_SECRET` raises at import unless the operator explicitly opts into dev mode with a separate variable. The dev-mode path generates a per-process random secret instead of using a hardcoded one, so even leaked dev-mode tokens cannot be used against another deployment. Add a startup banner that prints the JWT secret's hash prefix (not the secret itself) so operators can confirm at runtime which key is in use.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-3qg8-5g3r-79v5
- https://github.com/MervinPraison/PraisonAI
