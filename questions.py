import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the GitLab namespace/project path, for example group/project
SOURCE_REPO = 'smartcontractkit/chainlink'
# todo: the name of the repository
REPO_NAME = 'chainlink'

run_number = os.environ.get('GITHUB_RUN_NUMBER', '0')


def get_cyclic_index(run_number, max_index=100):
    """Convert run number to a cyclic index between 1 and max_index"""
    return (int(run_number) - 1) % max_index + 1


def load_repository_urls():
    """Load repository URLs from repositories.json."""
    repo_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "repositories.json")
    if not os.path.exists(repo_file):
        return []

    try:
        with open(repo_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    if not isinstance(data, list):
        return []

    return [url for url in data if isinstance(url, str) and url.strip()]


if run_number == "0":
    BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"
else:
    repository_urls = load_repository_urls()
    if repository_urls:
        run_index = get_cyclic_index(run_number, len(repository_urls))
        BASE_URL = repository_urls[run_index - 1]
    else:
        BASE_URL = f"https://deepwiki.com/{SOURCE_REPO}"

scope_files = [
    # =================================================================================
    # Node API authentication: session, token, external-initiator and route middleware
    # =================================================================================
    "core/web/router.go",
    "core/web/middleware.go",
    "core/web/auth/auth.go",
    "core/web/auth/gql.go",
    "core/web/auth/helpers.go",
    "core/web/cookies.go",
    "core/web/api.go",
    "core/web/common.go",
    "core/web/helpers.go",

    # =================================================================================
    # Session lifecycle, MFA and user identity storage
    # =================================================================================
    "core/sessions/authentication.go",
    "core/sessions/session.go",
    "core/sessions/user.go",
    "core/sessions/webauthn.go",
    "core/sessions/localauth/orm.go",
    "core/sessions/localauth/reaper.go",
    "core/sessions/ldapauth/ldap.go",
    "core/sessions/ldapauth/client.go",
    "core/sessions/ldapauth/sync.go",
    "core/sessions/oidcauth/oidc.go",
    "core/web/sessions_controller.go",
    "core/web/webauthn_controller.go",
    "core/web/user_controller.go",

    # =================================================================================
    # GraphQL surface: role enforcement on queries and mutations
    # =================================================================================
    "core/web/resolver/auth.go",
    "core/web/resolver/api_token.go",
    "core/web/resolver/user.go",
    "core/web/resolver/query.go",
    "core/web/resolver/mutation.go",

    # =================================================================================
    # REST controllers reachable with view/run/edit roles
    # =================================================================================
    "core/web/pipeline_runs_controller.go",
    "core/web/jobs_controller.go",
    "core/web/external_initiators_controller.go",
    "core/web/bridge_types_controller.go",
    "core/web/keys_controller.go",
    "core/web/eth_keys_controller.go",
    "core/web/csa_keys_controller.go",
    "core/web/dkg_recipient_keys_controller.go",
    "core/web/workflow_keys_controller.go",
    "core/web/vault_controller.go",
    "core/web/evm_transfer_controller.go",
    "core/web/replay_controller.go",
    "core/web/config_controller.go",
    "core/web/log_controller.go",
    "core/web/loop_registry.go",

    # =================================================================================
    # Response presenters: secret/credential redaction before serialization
    # =================================================================================
    "core/web/presenters/user.go",
    "core/web/presenters/eth_key.go",
    "core/web/presenters/csa_key.go",
    "core/web/presenters/bridges.go",
    "core/web/presenters/external_initiators.go",
    "core/web/presenters/vault.go",
    "core/web/presenters/job.go",

    # =================================================================================
    # External initiator and bridge credential handling
    # =================================================================================
    "core/bridges/external_initiator.go",
    "core/bridges/bridge_type.go",
    "core/bridges/orm.go",
    "core/bridges/cache.go",

    # =================================================================================
    # Gateway transport: internet-facing HTTP/WS servers and message envelope auth
    # =================================================================================
    "core/services/gateway/network/httpserver.go",
    "core/services/gateway/network/wsserver.go",
    "core/services/gateway/network/wsconnection.go",
    "core/services/gateway/network/handshake.go",
    "core/services/gateway/api/message.go",
    "core/services/gateway/api/jsonrpccodec.go",
    "core/services/gateway/api/codec.go",
    "core/services/gateway/gateway.go",
    "core/services/gateway/multihandler.go",
    "core/services/gateway/connectionmanager.go",
    "core/services/gateway/common/utils.go",

    # =================================================================================
    # Gateway handlers: user request authorization, quotas and response routing
    # =================================================================================
    "core/services/gateway/handlers/confidentialrelay/handler.go",
    "core/services/gateway/handlers/confidentialrelay/bundler.go",
    "core/services/gateway/handlers/capabilities/v2/shard_endpoints.go",
    "core/services/gateway/handlers/handler.go",
    "core/services/gateway/handlers/capabilities/webapi.go",
    "core/services/gateway/handlers/capabilities/handler.go",
    "core/services/gateway/handlers/capabilities/v2/http_handler.go",
    "core/services/gateway/handlers/capabilities/v2/http_trigger_handler.go",
    "core/services/gateway/handlers/capabilities/v2/workflow_metadata_handler.go",
    "core/services/gateway/handlers/capabilities/v2/response_cache.go",
    "core/services/gateway/handlers/vault/handler.go",
    "core/services/gateway/handlers/vault/aggregator.go",
    "core/services/gateway/handlers/common/requestcache.go",
    "core/services/gateway/handlers/common/callback.go",
    "core/services/gateway/handlers/common/message_util.go",
]


target_scopes = [
    "Critical. An unprivileged node-API caller (view or run role, or an unauthenticated client) authenticates as or acts with the rights of a higher role by exploiting session creation, cookie/token handling, WebAuthn MFA enforcement, or the Authenticate middleware chain in core/web/auth, gaining admin control of the node.",
    "Critical. A low-privileged authenticated user (view/run) reaches an edit- or admin-gated REST or GraphQL operation because the route wiring, RequiresEditRole/RequiresAdminRole wrappers, or resolver-level role checks are missing, ordered wrongly, or bypassable, letting them create jobs, move funds, or mutate node state.",
    "Critical. Any unprivileged caller exfiltrates node key material or credentials - private keys, key export bundles, vault/DKG secrets, session or API tokens, bridge/external-initiator secrets - through a controller, presenter, GraphQL resolver, or log path that fails to redact or over-authorize, enabling theft of oracle identity or funds.",
    "Critical. A holder of a restricted API token or external-initiator credential escalates beyond its intended surface by exploiting AuthenticateExternalInitiator or AuthenticateByToken HMAC/constant-time comparison, initiator-to-job binding, or token lookup, and triggers or manipulates jobs and runs they were never authorized for.",
    "Critical. An internet-facing gateway request from an arbitrary externally-owned address is accepted as another user's request because message signature recovery, sender/DON-ID/method binding, or envelope validation in core/services/gateway/api is unsound, letting the attacker impersonate a subscribed user and consume or redirect their capability execution.",
    "Critical. An unauthorized gateway user obtains vault or confidential-relay secrets, or forces the vault handler/aggregator to route a decrypted or signed response to the wrong requester, by exploiting owner/permission checks, request-id derivation, or response correlation in the vault handler.",
    "High. An unprivileged gateway user bypasses Functions allowlist or subscription checks - stale allowlist state, address normalization/case handling, balance or tier accounting, or per-user quotas - and gets free or unauthorized DON execution at another subscriber's expense.",
    "High. A run- or edit-role user causes unauthorized on-chain or financial action - triggering pipeline runs on jobs they must not run, replaying blocks, or submitting transfers/transactions - by exploiting job-ID resolution, run-request parsing, or missing ownership binding in the pipeline run and transfer controllers.",
    "High. An unauthenticated or unprivileged caller extracts sensitive node internals - full config with secrets, LOOP plugin registry/debug endpoints, health and log endpoints, or job spec contents including bridge credentials - from routes that lack the intended authentication or role gate.",
    "High. An unprivileged gateway or API client corrupts shared server state for other users - request/response cache key collisions, callback map or connection-manager entry hijacking, workflow metadata poisoning, or duplicate request-id reuse - so another user's request is answered with attacker-controlled data.",
    "Critical/High blind spot. An unprivileged actor abuses a trust assumption the design never wrote down: an entry point whose authorization is enforced only at a later layer that can be skipped, an identity (user, API token, external initiator, gateway sender, workflow owner) that is trusted after being derived rather than verified, a credential or role whose revocation, rotation, deletion or downgrade is not honored by live sessions, caches or long-lived connections, or a request field that silently crosses from one authenticated context into another - producing full authentication bypass, undeletable access, or action attributed to a victim identity.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate exploit-focused audit and fuzzing questions for one chainlink target.

    ```
    target_file format:
    "'File Name: core/web/auth/auth.go -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate exploit-focused security audit questions for this exact chainlink target:

    {target_file}

    Project focus:
    chainlink is the Chainlink node. Focus on surfaces an outsider or low-privileged user can reach: the node REST/GraphQL API and its session, API-token, external-initiator and role (view/run/edit/admin) authentication, key and secret presentation, and the internet-facing gateway (HTTP/WS servers, signed message envelopes, Functions allowlist/subscriptions, webAPI/HTTP trigger handlers, vault handler, request caches).

    Rules:
    * Treat `File Name:` as the exact file/package.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact Go symbols (func, method, struct, field) when possible.
    * Attacker is unprivileged only: an unauthenticated HTTP client of the node API or gateway, a view/run-role node user, a restricted API token or external-initiator credential holder, or any externally-owned address sending signed gateway requests.
    * Attacker is NOT a node operator, admin-role user, DB/host owner, or CI/deployment actor. Never assume a malicious node, malicious DON/OCR peer, malicious oracle, network-layer attacker, misconfiguration, leaked admin credentials, or social engineering.
    * Ignore test files, mocks, fuzz harnesses, docs, generated code, config/TOML-only findings, and dependency-only issues.
    * Ignore findings that need non-default builds or disabled-by-default features unless reachable on default configuration.
    * Generate 30 to 40 high-signal questions.
    * At least 70% must target authentication bypass, role/authorization bypass, credential or key material disclosure, request impersonation via signature/sender validation, allowlist or quota bypass, or cross-user state and response confusion.
    * Every question must be testable by unit test, table test, or Go HTTP/handler integration test.
    * Avoid generic checklist questions and repeated root causes.

    Core invariants:
    * Authentication is sound: only a valid unexpired session, API token, or external-initiator credential authenticates, and identity cannot be forged, replayed, or confused across auth methods.
    * Authorization is exact: every route and resolver enforces the minimum role it declares; a view/run user can never reach edit/admin behavior.
    * Secrets never leave: private keys, vault/DKG material, tokens, and bridge/EI credentials are redacted in every response, error, and log.
    * Requests are bound: a gateway or API request is attributable to exactly one authenticated sender and one authorized job, subscription, or workflow.
    * Isolation holds: one user's request, cache entry, callback, or connection cannot be read, answered, or overwritten by another.

    Each question must include:
    1. target function/method;
    2. attacker action (a concrete HTTP, GraphQL, or gateway request);
    3. preconditions (the minimal credential or role held);
    4. request sequence;
    5. invariant tested;
    6. scoped impact;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Function: symbol_or_method] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger REQUEST_SEQUENCE, violating INVARIANT, causing scoped impact: SCOPE_IMPACT? Proof idea: unit/integration test PARAMETERS and assert AUTHENTICATION_SOUNDNESS, AUTHORIZATION_EXACTNESS, SECRET_CONFINEMENT, REQUEST_BINDING, or ISOLATION.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate a focused chainlink exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: an unauthenticated client of the node API or gateway, a view/run-role user, a restricted API token or external-initiator credential holder, or any address sending signed gateway requests. No operator, admin, host, or database access; no leaked admin credentials or social engineering.
- Reject malicious-node, malicious-DON/OCR-peer, malicious-oracle, network-layer, host-level, operator-only, and misconfiguration-only paths.
- Reject anything depending only on test/mock/fuzz/docs/config/generated files, dependency bugs alone, or best-practice cleanup without exploitable impact.
- Focus on real node compromise: authentication bypass, role/authorization bypass, key or secret disclosure, request impersonation, allowlist/quota bypass, unauthorized job run or fund movement, or cross-user response confusion.

## Validate
- Trace the exact reachable path from the attacker's request (HTTP route, GraphQL operation, or gateway message) into the affected function.
- Check whether the auth middleware, role wrapper, presenter redaction, signature verification, or existing validation already stops it.
- Accept only concrete privilege escalation, unauthorized action on another user's job/subscription/secret, credential exposure, or attacker-controlled data returned to another user.
- Require exact file/function support and a reproducible Go unit or handler-level integration PoC.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[Code path, root cause, attacker request inputs, exploit flow, and why checks fail]

### Impact Explanation
[Concrete scoped impact and matching Chainlink bounty impact class]

### Likelihood Explanation
[Preconditions, minimal credential or role needed, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[Go unit/table/handler integration test plan with expected assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for chainlink security claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- Reject malicious-node, malicious-DON/OCR-peer, network-layer, host-level, operator-only, misconfiguration, leaked-credential, dependency-only, docs/style, generated-file, and test/mock/config-only issues.
- Reject if the exploit needs operator or admin-role access, database or host access, victim social engineering, an impossible setup, or behavior outside what an unprivileged client can send to the node API or gateway.
- Reject if the bug was fixed, acknowledged, or publicly disclosed already, per the eligibility rules.
- A valid report must be triggerable by an unprivileged actor, unless the claim proves escalation from an unprivileged starting point.
- The final impact must map to an in-scope Chainlink impact such as node API authentication or role bypass, key/secret exfiltration, unauthorized job run or fund movement, gateway request impersonation, allowlist or subscription bypass, or cross-user response corruption.
- Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, function, and line/code references.
2. Clear root cause and broken security assumption.
3. Reachable exploit path: preconditions (minimal credential/role) -> attacker request -> trigger -> bad result.
4. Existing auth middleware, role wrappers, signature checks, redaction, and validation reviewed and shown insufficient.
5. Concrete in-scope impact with realistic likelihood.
6. Reproducible proof path: Go unit PoC, handler integration test, or exact HTTP/GraphQL/gateway request steps against a local node.
7. No obvious rejection reason from SECURITY.md, known issues, privilege assumptions, or scope exclusions.

## Silent Triage Questions
Before output, internally answer:
- Can an unprivileged client trigger this through normal requests without operator, admin, or host access?
- Does the code actually behave as claimed on default configuration?
- Is the impact caused by this code, not by a malicious node, peer, or dependency alone?
- Is the bypass, disclosure, impersonation, or unauthorized action concrete, not hypothetical?
- Would a Chainlink bounty triager accept the proof?
- What exact test would prove it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([File: file_path])

## Summary
[2-3 sentence summary of the bug and impact]

## Finding Description
[Exact code path, root cause, exploit flow, and why existing checks fail]

## Impact Explanation
[Concrete in-scope impact, severity rationale, and Chainlink bounty category]

## Likelihood Explanation
[Attacker capability, required credential or role, feasibility, repeatability]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or Go unit/integration test plan]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for chainlink.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope production repo context only. Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only unprivileged-actor analogs in node API authentication and roles, session/token/external-initiator handling, secret redaction, or the internet-facing gateway (message envelopes, allowlist/subscriptions, handlers, caches).
- Reject malicious-node, malicious-peer, network-layer, operator-only, mocked-only paths, dependency-only bugs, and no-impact analogs.

## Validate
- Map the bug class to the strongest reachable chainlink path from an unprivileged client request.
- Prove root cause with exact file/function support.
- Accept only concrete authentication or role bypass, key/secret disclosure, request impersonation, allowlist or quota bypass, unauthorized job run or fund movement, or cross-user response confusion.

## Output (Strict)
If valid analog exists, output:

### Title
[Clear vulnerability statement] - ([File: file_path])

### Summary
### Finding Description
### Impact Explanation
### Likelihood Explanation
### Recommendation
### Proof of Concept

If not, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt
