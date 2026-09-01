import json
import os

from decouple import config

# todo: if scope_files is: 500 > 50, 300 > 30 , 100 > 10
MAX_REPO = 20
# todo: the GitLab namespace/project path, for example group/project
SOURCE_REPO = 'Shopify/shopify-api-ruby'
# todo: the name of the repository
REPO_NAME = 'shopify-api-ruby'

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
    # LENS: TRUST BOUNDARY AND IDENTITY BINDING.
    # This gem is the authentication layer of every Shopify app that embeds it. Every file
    # below turns attacker-reachable bytes - query params, cookies, HTTP headers, a JWT, a
    # webhook body, a shop domain string - into one of three decisions: is this request
    # authentic, which shop/user does it belong to, and which host receives the merchant's
    # access token or the app's client_secret. A question belongs here only if it can be
    # closed by a binding that must hold between what was signed and what is acted upon.
    # =================================================================================

    # -- Signature verification and everything it is supposed to cover ----------------
    # HmacValidator is the single arbiter of authenticity for BOTH the OAuth callback and
    # every inbound webhook, and it only ever sees `to_signable_string`. Anything a caller
    # trusts that is not inside that string is unauthenticated input wearing a valid HMAC.
    "lib/shopify_api/utils/hmac_validator.rb",
    "lib/shopify_api/utils/verifiable_query.rb",
    "lib/shopify_api/auth/oauth/auth_query.rb",
    "lib/shopify_api/webhooks/request.rb",

    # -- Who the request claims to be, and where the credential is sent ---------------
    # JwtPayload turns a session token into a shop string; ShopValidator is the only thing
    # standing between an attacker-supplied host and an outbound request carrying
    # client_secret or X-Shopify-Access-Token; SessionUtils mints the storage key the host
    # app uses to load that credential back.
    "lib/shopify_api/auth/jwt_payload.rb",
    "lib/shopify_api/utils/shop_validator.rb",
    "lib/shopify_api/utils/session_utils.rb",
    "lib/shopify_api/auth/session.rb",
    "lib/shopify_api/auth/auth_scopes.rb",

    # -- The credential-issuing flows -------------------------------------------------
    # begin_auth / validate_auth_callback (state cookie, HMAC, code redemption),
    # token exchange, client credentials and refresh - the four ways an access token is
    # obtained and bound to a shop.
    "lib/shopify_api/auth/oauth.rb",
    "lib/shopify_api/auth/oauth/session_cookie.rb",
    "lib/shopify_api/auth/oauth/access_token_response.rb",
    "lib/shopify_api/auth/token_exchange.rb",
    "lib/shopify_api/auth/client_credentials.rb",
    "lib/shopify_api/auth/refresh_token.rb",

    # -- Where the token actually goes on the wire ------------------------------------
    # HttpClient builds `https://#{api_host || session.shop}` and attaches the access token
    # to it; Rest::Admin and Rest::Base build the path from caller and response data;
    # GraphqlProxy forwards a browser-supplied body to the Admin API on the app's session.
    "lib/shopify_api/clients/http_client.rb",
    "lib/shopify_api/clients/http_request.rb",
    "lib/shopify_api/clients/rest/admin.rb",
    "lib/shopify_api/clients/graphql/client.rb",
    "lib/shopify_api/rest/base.rb",
    "lib/shopify_api/utils/graphql_proxy.rb",
    "lib/shopify_api/utils/http_utils.rb",

    # -- Inbound webhook dispatch and global configuration ----------------------------
    "lib/shopify_api/webhooks/registry.rb",
    "lib/shopify_api/webhooks/registrations/http.rb",
    "lib/shopify_api/context.rb",
    "lib/shopify_api/logger.rb",

    # =================================================================================
    # NOT IN THIS VARIANT:
    # * lib/shopify_api/rest/resources/** - machine-generated per-version REST resource
    #   classes. Generated code, no security decision, out of scope.
    # * lib/shopify_api/errors/** - message-only exception classes.
    # * test/**, sorbet/**, docs/**, bin/, Rakefile, *.gemspec, Gemfile*, *.md, *.yml.
    # =================================================================================
]


target_scopes = [
    "Critical. THE STATE COOKIE IS NOT BOUND TO A SHOP. `begin_auth` mints `state = SecureRandom.alphanumeric(15)` and stores it in a `SessionCookie` that carries the nonce and nothing else - not the shop it was issued for, not `is_online`, not the scope. `validate_auth_callback` then only asserts `state == auth_query.state`. Show that a callback validly signed for shop B completes an authorization the browser began for shop A, so the victim's browser is handed a `Session` for a shop the attacker controls, or the attacker's browser drives the app into storing a session it did not begin. Identity that breaks: shop passed to `begin_auth` == `auth_query.shop` at callback.",

    "Critical. THE HMAC DOES NOT COVER THE REQUEST. `AuthQuery#to_signable_string` signs exactly five fields - code, host, shop, state, timestamp - via `URI.encode_www_form`. Anything else in the real callback URL is unauthenticated, and `timestamp` is verified as a string but never compared to `Time.now`. Show a callback whose HMAC verifies while a field the host app or this gem acts on differs from what Shopify signed: an extra or duplicated query key, a value whose encoding survives `encode_www_form` differently than it arrived, or a replay of a months-old signed callback. Identity: set of fields acted upon == set of fields inside `to_signable_string`.",

    "Critical. THE WEBHOOK SIGNATURE COVERS ONLY THE BODY. `Webhooks::Request#to_signable_string` returns `@raw_body`; `topic`, `shop-domain`, `api-version` and `webhook-id` come from headers that no signature covers. `Registry.process` selects the handler by `request.topic` and hands `shop: request.shop` straight into `WebhookMetadata`, which is how the host app decides whose records to mutate. Show that anyone who obtains one validly signed body - their own shop's webhook, delivered to their own registered endpoint - can relabel it to another topic and another shop and have the app act on it as that tenant. Identity: shop and topic the handler acts on == shop and topic authenticated by the HMAC.",

    "Critical. THE HMAC IS NORMALIZED BEFORE IT IS COMPARED. `Request#hmac` computes `Digest.hexencode(Base64.decode64(header))`, and `Base64.decode64` silently drops characters outside the alphabet and tolerates missing padding, so many distinct header values collapse to the same digest, while `HmacValidator.validate_signature` calls `OpenSSL.secure_compare` on the result. Separately, `to_signable_string` returns the body as the framework handed it over. Show a divergence between the bytes verified and the bytes later returned by `parsed_body` - an encoding change, a truncated or re-read body, a trailing-byte variant - so a handler processes content that was never signed. Identity: bytes passed to `compute_signature` == bytes passed to `JSON.parse`.",

    "Critical. THE SHOP FROM A SESSION TOKEN IS NEVER VALIDATED AS A SHOPIFY DOMAIN. `JwtPayload#shop` is `@dest.gsub(\"https://\", \"\")` - an unanchored global substitution on a claim the constructor never checks against `TRUSTED_SHOPIFY_DOMAINS`, and it never asserts that `iss` and `dest` name the same shop. `TokenExchange.exchange_token` feeds that string into `Session.new(shop:)`, which `HttpClient` turns into `https://#{session.shop}` for a POST carrying `client_id` and `client_secret`. Show a `dest` or `iss` value reachable under a token this app's secret verifies that redirects the credential POST, or that binds the returned access token to the wrong shop key. Identity: host receiving `client_secret` ∈ TRUSTED_SHOPIFY_DOMAINS, and session key shop == authenticated shop.",

    "Critical. THE OAUTH CALLBACK SHOP IS NEVER SANITIZED. `ClientCredentials`, `RefreshToken` and `migrate_to_expiring_token` all call `Utils::ShopValidator.sanitize!`, but `Oauth.begin_auth` (`auth_base_uri` -> `\"https://#{shop}/admin\"`) and `Oauth.validate_auth_callback` (`Session.new(shop: auth_query.shop)`, then `Session.from(shop: auth_query.shop, ...)`) do not. Show that the shop string travelling through the OAuth flow reaches `HttpClient`'s `@base_uri`, the authorize redirect, or the stored session id without ever passing the validator, and turn that into exfiltration of `client_secret` and the authorization `code`, or a session stored under a shop key the app will later serve to the wrong tenant.",

    "Critical. THE VALIDATOR ITSELF CAN BE TALKED PAST. `ShopValidator.sanitize_shop_domain` accepts a host when `trusted_domain == uri.domain`, and when `unified_admin?` (first label literally `admin`) holds it returns `\"#{uri.path.split(\"/\").last}.myshopify.com\"` built from an unvalidated path segment. Input is only downcased, stripped, rejected on `@`, and given a scheme. Probe the gap between what `Addressable::URI` calls `host`/`domain` and what an HTTP client resolves: a trailing dot, an embedded port or credentials, percent-encoded or backslash separators, IDN and Unicode-normalizing labels, a path segment that is itself a hostname or empty. Any input that returns from `sanitize!` but is not a Shopify shop becomes the destination of the merchant's access token.",

    "Critical. THE SESSION ID IS DERIVED FROM UNAUTHENTICATED BYTES. `SessionUtils.current_session_id` returns `cookies[\"shopify_app_session\"]` verbatim as the storage key whenever the app is non-embedded, and for embedded apps too whenever no `shopify_id_token` is presented - the gem never verifies that cookie against `Context.api_secret_key`. On the token path it builds `\"#{shop}_#{payload.sub}\"` or `\"offline_#{shop}\"` by string interpolation of unvalidated values. Show that an attacker who supplies a chosen cookie value, or a shop or `sub` containing the separator, loads a session - and therefore an access token - belonging to a different merchant or a different user of the same shop. Identity: session id derived only from bytes authenticated under the app secret.",

    "Critical. THE TOKEN IS ATTACHED BEFORE THE DESTINATION IS SETTLED. `HttpClient#initialize` sets `@base_uri = \"https://#{api_host || session.shop}\"` and unconditionally adds `X-Shopify-Access-Token`; `request_url` is plain interpolation of `request.path`; `Rest::Admin#request_url` re-roots the URL at `@base_uri` for any path starting with `admin/`; `Rest::Base.get_path` interpolates ids taken from caller input and from API response data into that path. Show a path or id value - traversal segments, a scheme or `//host`, an encoded `?` or `#` - that moves the authenticated request to an endpoint or host the caller never intended, and state what the access token reaches. Identity: the URL actually requested == base_uri + intended resource path, with the token only ever leaving for the session's own shop.",

    "High. AUTHORIZATION STATE IS TRUSTED WITHOUT BEING TRUE. `Session#expired?` returns false whenever `@expires` is nil, so a session that never learned its expiry is permanently valid; `AuthScopes#covers?` compares the caller's `compressed_scopes` against `expanded_scopes` grown by `implied_scope`, whose regex `\\A(unauthenticated_)?write_(.*)\\z` manufactures a read scope from any string shaped like a write scope; scope strings are split on `,` with no validation of the tokens. `GraphqlProxy.proxy_query` then forwards a caller-supplied GraphQL body on the merchant's online session with `session.online?` as its only gate, and `HttpUtils.normalize_headers` decides the content type by downcasing and rewriting caller-supplied header names. Show a request that passes a scope, expiry or proxy check it should fail, and name the merchant data it reaches.",

    "Critical. THE MISSING BINDING - what nobody built. Nothing in this gem ever asserts that the shop a request authenticates as, the shop key a session is stored under, and the host that receives the access token are the same value; there is no single choke point where an untrusted shop string is sanitized once, and no check that a session loaded from storage matches the authenticated shop of the current request. Identify the FIRST point at which a shop string from an unauthenticated source (an OAuth callback param, a webhook header, a JWT claim, a cookie) becomes a session key or an outbound request host without passing `ShopValidator`, prove it with one minitest + WebMock test that asserts the request host and the stored session id, and show that once the two diverge the gem never notices and the host app has no API with which to detect it.",
]


scope_scan = [
]


def question_generator(target_file: str) -> str:
    """
    Generate identity-binding audit questions for one shopify-api-ruby target.

    ```
    target_file format:
    "'File Name: lib/shopify_api/utils/shop_validator.rb -> Scope: Critical. ...'"
    """

    prompt = f"""
    ```

    Generate authentication and trust-boundary security audit questions for this exact
    shopify-api-ruby target:

    {target_file}

    Project focus:
    This gem is the authentication layer of every Shopify app that embeds it. Untrusted bytes
    enter through four doors: the OAuth callback query (`AuthQuery`), an inbound webhook
    (`Webhooks::Request` - body plus unsigned headers), a session token / JWT (`JwtPayload`),
    and the `shopify_app_session` cookie (`SessionUtils`). From those bytes the gem decides
    (a) is the request authentic - `HmacValidator` over `to_signable_string` only, (b) which
    shop and user it belongs to - a string interpolated into a session id, and (c) which host
    receives `client_secret` or `X-Shopify-Access-Token` - `HttpClient`'s
    `https://#{{api_host || session.shop}}`. `ShopValidator.sanitize!` guards only some of
    those paths. Anything trusted but unsigned, or used as a host but unvalidated, is the bug.

    Rules:
    * Treat `File Name:` as the exact file.
    * Treat `Scope:` as the ONLY impact to target.
    * Assume full repo context is accessible.
    * Do not ask for code or say anything is missing.
    * Use exact Ruby symbols (module, class, method, constant, ivar) as they appear in the file.
    * EVERY question must close on a binding that must hold across a call. State it explicitly.
      Narrative questions with no stated binding are rejected.
    * Attacker is unprivileged only: any internet user who can send HTTP requests to an app
      built on this gem. They may create their own development shop, install the app on it,
      register their own webhook endpoint, receive their own validly signed callbacks and
      webhooks, run their own server, and control query params, headers, cookies, bodies,
      redirect targets and request ordering.
    * Attacker is NOT the app developer, a Shopify employee, the victim merchant or their
      staff, and never holds `api_secret_key`, `old_api_secret_key`, an access token, or any
      leaked credential. No TLS interception, no local or physical access, no compromised
      dependency, no social engineering.
    * Assume the host app uses this gem as documented in README.md and docs/. The bug must be
      in this gem's code, not in a hypothetical caller misusing it.
    * PROGRAM EXCLUSIONS - a question landing in any of these wastes the whole batch:
      - lib/shopify_api/rest/resources/** is machine-generated per-version code and is OUT OF
        SCOPE, as are test/**, sorbet/**, docs/**, *.md, *.yml, *.gemspec and Gemfile*.
      - Denial of service, rate limiting, retry/backoff behaviour, resource exhaustion,
        unbounded collections and memory hygiene are OUT OF SCOPE.
      - Vulnerabilities in third-party gems (jwt, httparty, addressable, openssl, zeitwerk)
        with no exploit path through this gem's own code are OUT OF SCOPE.
      - Also excluded: leaked keys or credentials, privileged accounts, best-practice notes,
        feature requests, missing security headers, self-XSS, theoretical findings with no
        demonstration, and anything requiring the attacker to already hold app secrets.
      - A weakness in this gem that lets an attacker manipulate a third-party library into
        unsafe behaviour remains fully in scope.
    * IN-SCOPE IMPACTS - every question must land on one and name it:
      Critical: authentication bypass (a forged webhook, callback or session token accepted);
      theft or exfiltration of a merchant access token, refresh token, authorization code or
      the app's `client_secret`; cross-tenant access - one shop or one staff user acting on
      another's data; remote code execution.
      High: server-side request forgery driving an authenticated request to an unintended
      host; session fixation or forced OAuth completion; scope or expiry check bypass;
      credential leakage into logs or error output.
    * Every question must be a concrete real-world scenario an unprivileged internet user can
      execute against a deployed app that embeds this gem. No speculative resource-hygiene,
      memory or unbounded-growth questions.
    * A raised exception is a finding only when it lets an unauthenticated request through, or
      leaks a secret in its message - say which.
    * Generate 30 to 40 high-signal questions.
    * At least 70% must land on a Critical impact - authentication bypass, credential theft,
      cross-tenant access or RCE - rather than a High one.
    * Every question must be testable by a minitest + WebMock/Mocha test under `test/` with no
      live shop and no network. Never propose testing against a real Shopify store.
    * Avoid generic checklist questions and repeated root causes.
    * Prefer questions that name TWO values that must be equal and ask whether they are: a
      field signed and a field acted on, a shop authenticated and a shop stored, a host
      validated and a host requested, bytes verified and bytes parsed, a scope granted and a
      scope accepted.

    Known dead ends - do NOT generate questions about these:
    * Anything needing `api_secret_key`, an access token, or any leaked credential.
    * A CVE in a dependency with no reachable path through this gem.
    * The host application choosing to ignore this gem's documented API.
    * Findings only reproducible against the generated REST resource classes or test helpers.
    * Timing, DoS, log volume, or a user harming only their own shop with no tenant boundary
      crossed and no credential exposed.

    Core bindings (each question must close on one):
    * SIGNATURE COVERAGE: every value acted on downstream is inside the string handed to
      `HmacValidator` via `to_signable_string`.
    * SHOP BINDING: the shop authenticated by the signature or JWT == the shop interpolated
      into the session id == the shop used as the request host.
    * CREDENTIAL DESTINATION: `client_secret`, an authorization code and
      `X-Shopify-Access-Token` leave only for a host that `ShopValidator` accepted.
    * SESSION DERIVATION: a session id is derived only from bytes authenticated under
      `Context.api_secret_key`.
    * AUTHORIZATION TRUTH: `covers?`, `expired?`, the state comparison and the proxy gate
      never return a permissive answer for a session that lacks the right.

    Each question must include:
    1. target class/method;
    2. attacker action (a concrete HTTP request with params, headers, cookies or body);
    3. preconditions (app configuration, embedded or not, existing session state);
    4. call sequence through the gem;
    5. the binding that breaks, written as an equality;
    6. scoped impact and whose credential or data is exposed;
    7. proof idea.

    Output only valid Python. No markdown. No explanations.

    questions = [
    "[File: {target_file}] [Method: class_or_method] Can an unprivileged ATTACKER_ACTION under PRECONDITIONS trigger CALL_SEQUENCE, breaking the binding BINDING_EQUALITY, causing scoped impact: SCOPE_IMPACT against PARTY? Proof idea: minitest + WebMock test PARAMETERS asserting SIGNATURE_COVERAGE, SHOP_BINDING, CREDENTIAL_DESTINATION, SESSION_DERIVATION, or AUTHORIZATION_TRUTH.",
    ]
    """
    return prompt


def audit_format(security_question: str) -> str:
    """
    Generate an identity-binding shopify-api-ruby exploit-validation prompt.
    """

    prompt = f"""# SECURITY AUDIT PROMPT

## Question
{security_question}

## Rules
- Use existing repo context only. Analyze only this question and scoped impact.
- Attacker is unprivileged only: any internet user who can send HTTP requests to an app built on this gem. They may create their own development shop, install the app on it, register their own webhook endpoint, receive their own validly signed callbacks and webhooks, run their own server, and control query params, headers, cookies, bodies, redirect targets and ordering. They never hold `api_secret_key`, `old_api_secret_key`, an access token or any leaked credential, and are not the app developer, a Shopify employee, or the victim merchant or their staff.
- Reject TLS interception, local or physical access, compromised dependencies, social engineering, and any path requiring app secrets.
- Assume the host app uses this gem as documented. The bug must be in this gem's code.
- OUT OF SCOPE, reject on sight: `lib/shopify_api/rest/resources/**` (machine-generated), `test/**`, `sorbet/**`, `docs/**`, `*.md`, `*.yml`, `*.gemspec`, `Gemfile*`; denial of service, rate limiting, retry behaviour, resource exhaustion and memory hygiene; third-party gem defects with no exploit path through this gem's own code; best-practice notes; feature requests; theoretical findings with no demonstration.
- The impact must be one of: Critical - authentication bypass (forged webhook, callback or session token accepted), theft or exfiltration of a merchant access token, refresh token, authorization code or the app's `client_secret`, cross-tenant access, or remote code execution; High - SSRF driving an authenticated request to an unintended host, session fixation or forced OAuth completion, scope or expiry check bypass, or credential leakage into logs or error output.
- Focus on real impact: a credential leaving for a host it should not, an unauthenticated value being trusted as authenticated, or one tenant's request touching another tenant's data.

## Validate
- Write the binding the question claims is broken as an explicit equality between two named values BEFORE tracing any code.
- Trace the exact reachable path from the attacker's HTTP request (params, headers, cookies, body, cookie jar, ordering) and record every read and write of `session.shop`, `session.id`, `session.access_token`, `@base_uri`, `@headers`, the signable string, the computed and received HMAC, and the JWT claims `iss`, `dest`, `aud`, `sub`, `exp`.
- Evaluate both sides of the equality before and after. If they still match, output no vulnerability.
- Check whether `HmacValidator.validate`, `ShopValidator.sanitize!`, the `state` comparison, `JwtPayload`'s `aud` check, `HttpRequest#verify`, `Context.setup?` / `private?` / `embedded?`, or Sorbet runtime typing already prevent the divergence.
- State what the attacker gains per request and whether it is repeatable against arbitrary victims.
- Require exact file/method support and a reproducible minitest + WebMock/Mocha proof under `test/` with no live shop.

## Output
If valid, output exactly:

### Title
[Bug statement] - ([File: file_path])

### Summary
[2-3 sentences]

### Finding Description
[The broken binding as an equality, the code path, root cause, the attacker's exact request, exploit flow, and why existing guards fail]

### Impact Explanation
[What is exposed or bypassed, which party, repeatability, blast radius across tenants, matching severity category]

### Likelihood Explanation
[Preconditions, app configuration required, attacker cost, feasibility, repeatability]

### Recommendation
[Specific fix]

### Proof of Concept
[minitest + WebMock test plan with the exact assertions on both sides of the binding]

If invalid, output exactly:
#NoVulnerability found for this question.

No extra text.
"""
    return prompt


def validation_format(report: str) -> str:
    """
    Generate a strict bounty-style validation prompt for shopify-api-ruby claims.
    """
    prompt = f"""# VALIDATION PROMPT

## Security Claim
{report}

## Rules
- Validate only the submitted claim.
- Check SECURITY.md and Researcher.Md for scope, exclusions, and valid impact classes.
- Do not create a new vulnerability if the submitted claim is weak or invalid.
- Do not upgrade severity unless the provided evidence proves the higher impact.
- A binding claim is only valid if the report states the broken equality between two named values and shows both sides concretely. Reject prose-only claims.
- Reject anything requiring `api_secret_key`, `old_api_secret_key`, an access token, leaked credentials, app developer or Shopify employee access, the victim merchant or their staff, TLS interception, local or physical access, a compromised dependency, or social engineering.
- OUT OF SCOPE, reject on sight: `lib/shopify_api/rest/resources/**` (machine-generated), `test/**`, `sorbet/**`, `docs/**`, `*.md`, `*.yml`, `*.gemspec`, `Gemfile*`; denial of service, rate limiting, retry behaviour, resource exhaustion and memory hygiene; third-party gem defects with no exploit path through this gem's own code; best-practice notes; feature requests; missing security headers; self-XSS; theoretical findings with no demonstration.
- The impact must be one of: Critical - authentication bypass, theft or exfiltration of a merchant access token, refresh token, authorization code or the app's `client_secret`, cross-tenant access, or remote code execution; High - SSRF with the app's credentials, session fixation or forced OAuth completion, scope or expiry check bypass, or credential leakage into logs or error output.
- Reject claims that depend on the host application ignoring this gem's documented API.
- Reject if the bug was already fixed, publicly disclosed, or is covered by an existing advisory or CHANGELOG entry for a supported version.
- Reject a divergence with no crossing of a tenant, credential or authentication boundary.
- A valid report must be triggerable by an unprivileged internet user against an app running the current released gem.
- A PoC is mandatory. Prefer #NoVulnerability over speculative reports.

## Required Validation Checks
All must pass:
1. Exact in-scope file, class/method, and line references.
2. The binding written explicitly as an equality, with both sides shown before and after.
3. Clear root cause: which unsigned field, which unvalidated host, which unauthenticated session key, or which missing check causes the divergence.
4. Reachable exploit path: preconditions -> attacker HTTP request -> gem call sequence -> observed divergence.
5. `HmacValidator`, `ShopValidator`, the `state` comparison, the JWT `aud` check, `HttpRequest#verify` and Context guards reviewed and shown insufficient.
6. Impact stated concretely: which credential or which tenant's data, and whether it is repeatable against arbitrary victims.
7. Reproducible proof: minitest + WebMock/Mocha test with the asserted values.

## Silent Triage Questions
Before output, internally answer:
- What exactly is the equality, and does it actually fail?
- Can an ordinary internet user trigger it with no secret and no privileged role?
- Is the flaw in this gem's code, not in a dependency or in a careless caller?
- What credential or whose data is exposed, and can it be repeated against other merchants?
- Would a Shopify HackerOne triager accept the exploit path?
- What exact test would prove it?

## Output
If valid, output exactly:

Audit Report

## Title
[Clear vulnerability statement] - ([File: file_path])

## Summary
[2-3 sentence summary of the broken binding and impact]

## Finding Description
[Exact code path, the equality, root cause, exploit flow, and why existing guards fail]

## Impact Explanation
[What is exposed or bypassed, affected party, repeatability, severity category]

## Likelihood Explanation
[Attacker capability, preconditions, app configuration, cost, feasibility]

## Recommendation
[Specific fix guidance]

## Proof of Concept
[Minimal reproducible steps or minitest + WebMock test plan with concrete assertions]

If invalid, output exactly:
#NoVulnerability found for this question.

Output only one of the two outcomes above. No extra text.
"""
    return prompt


def scan_format(report: str) -> str:
    """
    Generate a short cross-project analog scan prompt for shopify-api-ruby.
    """
    prompt = f"""# ANALOG SCAN PROMPT

## External Report
{report}

## Rules
- Use in-scope library context only (`lib/shopify_api/**`, excluding `lib/shopify_api/rest/resources/**`). Do not ask for code or claim missing files.
- Use the external report only as a bug-class hint, not as proof.
- Keep only unprivileged-internet-user analogs that break an identity binding: a field acted on but not covered by the HMAC, a shop authenticated versus the shop stored as a session key, a host validated versus the host that receives the access token or `client_secret`, bytes verified versus bytes parsed, a JWT claim trusted without being bound, a session id derived from unauthenticated bytes, or a scope or expiry check that answers permissively.
- OUT OF SCOPE, reject on sight: `lib/shopify_api/rest/resources/**` (machine-generated), `test/**`, `sorbet/**`, `docs/**`, `*.md`, `*.yml`, `*.gemspec`, `Gemfile*`; denial of service, rate limiting, retry behaviour, resource exhaustion and memory hygiene; third-party gem defects with no exploit path through this gem's own code; anything requiring `api_secret_key`, an access token, leaked credentials, a privileged account, TLS interception, local access or social engineering; best-practice notes; feature requests; theoretical findings.
- The impact must be one of: Critical - authentication bypass, theft or exfiltration of a merchant access token, refresh token, authorization code or the app's `client_secret`, cross-tenant access, or remote code execution; High - SSRF with the app's credentials, session fixation or forced OAuth completion, scope or expiry check bypass, or credential leakage into logs or error output.
- Reject analogs that depend on the host application ignoring this gem's documented API, and analogs with no credential, tenant or authentication boundary crossed.

## Validate
- Map the bug class to the strongest reachable path in this gem and state the binding it would break as an equality.
- Evaluate both sides before and after the attacker's request sequence.
- Prove root cause with exact file/method support.
- Accept only concrete authentication bypass, credential exfiltration, cross-tenant access, RCE, or SSRF carrying the app's credentials.

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
