# [H] @fedify/fedify has Improper Authentication and Incorrect Authorization

## Summary
Severity: High
Advisory: GHSA-6jcc-xgcr-q3h4
CVE: CVE-2025-54888
CWE: CWE-287, CWE-863
Ecosystem: npm
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-08
Source: https://github.com/advisories/GHSA-6jcc-xgcr-q3h4
Type: github-advisory

## Affected
- npm: `@fedify/fedify` — affected >=0 <1.3.20
- npm: `@fedify/fedify` — affected >=1.4.0-dev.585 <1.4.13
- npm: `@fedify/fedify` — affected >=1.5.0-dev.636 <1.5.5
- npm: `@fedify/fedify` — affected >=1.6.0-dev.754 <1.6.8
- npm: `@fedify/fedify` — affected >=1.7.0-pr.251.885 <1.7.9
- npm: `@fedify/fedify` — affected >=1.8.0-dev.909 <1.8.5

## Details
### Summary
 An authentication bypass vulnerability allows any unauthenticated attacker to impersonate any ActivityPub actor by sending forged activities signed with their own keys. Activities are processed before verifying the signing key belongs to the claimed actor, enabling complete actor impersonation across all Fedify instances

### Details
The vulnerability exists in handleInboxInternal function in fedify/federation/handler.ts. The critical flaw is in the order of operations:

  1. Line 1712: routeActivity() is called first, which processes the activity (either immediately or by adding to queue)
  2. Line 1730: Authentication check (doesActorOwnKey) happens AFTER processing

```ts
  // fedify/federation/handler.ts:1712-1750
  const routeResult = await routeActivity({  // ← Activity processed here
    context: ctx,
    json,
    activity,
    recipient,
    inboxListeners,
    inboxContextFactory,
    inboxErrorHandler,
    kv,
    kvPrefixes,
    queue,
    span,
    tracerProvider,
  });

  if (
    httpSigKey != null && !await doesActorOwnKey(activity, httpSigKey, ctx)  // ← Auth check too late
  ) {
    // Returns 401, but activity already processed
    return new Response("The signer and the actor do not match.", {
      status: 401,
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  }
```

By the time the 401 response is returned, the malicious activity has already been processed or queued.

### PoC

  1. Create an activity claiming to be from any actor:
```ts
  const maliciousActivity = {
    "@context": "https://www.w3.org/ns/activitystreams",
    "type": "Create",
    "actor": "https://victim.example.com/users/alice",  // Impersonating victim
    "object": {
      "type": "Note",
      "content": "This is a forged message!"
    }
  }
```
  2. Sign the HTTP request with attacker's key (not the victim's):
```ts
  // Sign with attacker's key: https://attacker.com/users/eve#main-key
  const signedRequest = await signRequest(request, attackerPrivateKey, attackerKeyId);
```
  3. Send to any Fedify inbox - the activity will be processed despite the key mismatch.

### Impact

Type: Authentication Bypass / Actor Impersonation

Who is impacted: All Fedify instances and their users

Consequences: Allows complete impersonation of any ActivityPub actor, enabling:
  - Sending fake posts/messages as any user
  - Creating/removing follows as any user
  - Boosting/sharing content as any user
  - Complete compromise of federation trust model

The vulnerability affects all Fedify instances but does not propagate to other ActivityPub implementations (Mastodon, etc.) which properly validate before processing.

## References
- https://github.com/fedify-dev/fedify/security/advisories/GHSA-6jcc-xgcr-q3h4
- https://nvd.nist.gov/vuln/detail/CVE-2025-54888
- https://github.com/fedify-dev/fedify/commit/14a2f8c6d2c3cbc00c3170a86ad3b7b8555c6847
- https://github.com/fedify-dev/fedify
