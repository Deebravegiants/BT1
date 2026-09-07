# [H] Blocky DNSSEC validation bypass and validation-cache scope pollution

## Summary
Severity: High
Advisory: GHSA-x845-2f78-7v36
CWE: CWE-346, CWE-807
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-x845-2f78-7v36
Type: github-advisory

## Affected
- Go: `github.com/0xERR0R/blocky` — affected >=0.28.0 <0.32.0

## Details
## Summary

Blocky accepts and caches forged DNS answers while `dnssec.validate: true` is enabled. The issue has two related exploit paths:

1. **Basic DNSSEC validation bypass.** If an untrusted upstream returns an unsigned positive answer for a DNSSEC-signed public domain, Blocky classifies the response as `Insecure` solely because the response contains no RRSIG records. It does not first check the DS/DNSKEY chain to determine whether the queried name is below a signed delegation. The forged unsigned answer is returned and cached.

2. **Validation-cache scope pollution through forged insecure proofs.** If a response contains some RRSIG material and enters RRset validation, an attacker-controlled response path can still cause Blocky to cache `ValidationResultInsecure` for the bare domain name by returning a DS response with no DS records and an unsigned NSEC/NSEC3 record in the authority section. Blocky treats the mere presence of NSEC/NSEC3 as authenticated DS absence and stores the resulting `Insecure` state without validating the parent-zone proof. That cached state is keyed only by domain name and can be reused for later responses and cache hits.

Both paths were reproduced through Blocky's real DNS listener using external UDP DNS client queries. In both reproductions, the malicious upstream was shut down before the second query; Blocky still returned the poisoned answer from its own cache.


## DNSSEC validation Configuration

The PoCs use Blocky's documented DNSSEC configuration model. This is not a misconfiguration.

Blocky's own documentation states that the basic DNSSEC configuration is:

```yaml
dnssec:
  validate: true
```

The documentation says this enables DNSSEC validation with default settings and built-in root trust anchors, and that Blocky will validate DNSSEC-signed domains. It also states that, when DNSSEC validation is enabled, Blocky will:

- set the DNSSEC OK bit on upstream queries;
- validate RRSIG records;
- verify the chain of trust from the root zone to the queried domain using DNSKEY and DS records;
- return SERVFAIL for bogus signatures;
- protect against cache poisoning, man-in-the-middle attacks, DNS spoofing, and forged denial-of-existence.

The implementation-side defaults match this documented usage:

- `config/dnssec.go` defines `DNSSEC.Validate` as the `dnssec.validate` option.
- `config/dnssec.go` documents `TrustAnchors []string` as custom trust anchors; an empty value uses built-in IANA root trust anchors.
- The PoCs set `cfg.DNSSEC.Validate = true` and do not override `TrustAnchors`, so they use the documented built-in root trust-anchor path.
- The PoCs use `config.NetProtocolTcpUdp` as the upstream transport, which is one of the documented upstream protocols.
- The cache configuration is normal Blocky behavior: `caching.maxTime >= 0` enables caching, and the PoCs set a positive `maxTime` only to make cache replay observable.

Therefore, the expected behavior for a signed public domain such as `cloudflare.com.` is not to accept an unsigned forged answer. A validating resolver must determine whether the name is covered by a signed delegation before treating missing signatures as `Insecure`.

## Threat models and attack paths

### Attack model 1: untrusted recursive upstream or upstream-path attacker

This is the direct DNSSEC threat model. DNSSEC validation is supposed to protect clients even when the recursive upstream response path is malicious, compromised, or tampered with.

The attacker can be:

- a malicious recursive upstream configured in Blocky;
- an attacker who can tamper with plaintext UDP/TCP DNS traffic between Blocky and its upstream;
- a compromised upstream resolver;
- a misrouted or attacker-controlled conditional upstream.

Attack steps:

1. The client queries Blocky for a DNSSEC-signed public name, for example `cloudflare.com. A`.
2. The attacker-controlled upstream returns an unsigned forged positive answer, for example `cloudflare.com. 120 IN A 203.0.113.77`.
3. Blocky observes that the response contains no RRSIG records.
4. Blocky returns `ValidationResultInsecure` without issuing target DS or DNSKEY queries.
5. The forged answer is returned to the client and cached.
6. Later clients receive the cached forged answer, even if the malicious upstream is no longer reachable.

This path is demonstrated by `attachments/external-dnssec-basic-bypass/main.go`.

### Attack model 2: forged insecure proof / validation-cache scope pollution

This path exercises the validator's insecure-proof and cache-scope logic. It is relevant when the response enters RRset validation and when different DNS views or response paths can seed DNSSEC state for the same domain name.

The attacker can be:

- an attacker-controlled recursive upstream;
- a network attacker who can tamper with DS/DNSKEY auxiliary queries;
- a conditional-forwarding or split-horizon configuration that causes the final answer and DNSSEC auxiliary lookups to come from different views;
- a malicious upstream group selected for DNSSEC auxiliary queries but not necessarily for the original user-facing answer.

Attack steps:

1. The client queries Blocky for `victim.signed.example. A`.
2. The attacker returns a poisoned A RR and an unrelated decoy RRSIG. The A RRset itself has no matching RRSIG, but the response contains some RRSIG material, so Blocky enters RRset validation instead of the simple `no RRSIG` branch.
3. Blocky attempts to determine whether `victim.signed.example.` is in a signed or unsigned zone by querying DS records.
4. The attacker returns a DS response with no DS records and an unsigned NSEC record in the authority section.
5. Blocky treats the mere presence of NSEC as authenticated DS absence, caches `ValidationResultInsecure` for the bare domain name, and accepts the unsigned A RRset.
6. The poisoned answer is returned and cached.
7. On later queries, Blocky reuses both the poisoned DNS response cache entry and the polluted validation status. The PoC confirms replay after the malicious upstream is shut down.

This path is demonstrated by `attachments/external-dnssec-cache-scope-pollution/main.go`.

## Details

### 1. `no RRSIG` is treated as `Insecure` before chain status is checked

In `resolver/dnssec/validator.go`, `ValidateResponse` dispatches as follows:

```go
switch {
case !v.hasAnySignatures(response):
    v.logger.Debugf("No RRSIG records found for %s - zone is unsigned", question.Name)
    result = ValidationResultInsecure
case len(response.Answer) > 0:
    result = v.validateAnswer(ctx, response, question)
...
}
```

The bug is the assumption that a response with no RRSIG records means the zone is unsigned. That assumption is not valid for a validating resolver. The resolver must first prove that the queried name is below an insecure delegation. For a signed domain, an unsigned positive answer should be `Bogus`, not `Insecure`.

The basic bypass PoC uses `cloudflare.com.`, a public DNSSEC-signed domain. Blocky returns `NOERROR` and the forged A record while issuing zero target DS and DNSKEY queries.

### 2. Cache writes happen before outer DNSSEC validation can reject or transform the response

`server/server.go:526-543` constructs the resolver chain with `dnssecResolver` before `cachingResolver` and includes a comment saying DNSSEC validation happens before caching:

```text
dnssecResolver, // DNSSEC validation BEFORE caching - validates all responses before they are cached
cachingResolver,
...
upstreamTree,
```

However, chained resolver execution is outer-to-inner. `DNSSECResolver.Resolve` first calls `r.next.Resolve`, and `CachingResolver.Resolve` writes cache entries on misses before control returns to the DNSSEC layer:

- `resolver/dnssec_resolver.go:88-96`: the DNSSEC resolver calls `r.next.Resolve(ctx, request)` before `ValidateResponse`.
- `resolver/caching_resolver.go:225-230`: on cache miss, the cache resolver calls the next resolver and then immediately calls `putInCache`.
- `resolver/caching_resolver.go:326-341`: the cache write only checks rcode and basic cacheability; it does not bind the entry to a DNSSEC validation result.

The practical result is that the DNS response cache can store data that has not yet survived final DNSSEC validation.

### 3. Validation cache is keyed only by bare domain name

`resolver/dnssec/chain.go:16-31` exposes:

```go
getCachedValidation(domain string)
setCachedValidation(domain string, result ValidationResult)
```

`resolver/dnssec/validator.go:638-642` reuses this cache for zone-security checks:

```go
if cached, found := v.getCachedValidation(domain); found {
    return cached
}
```

The key does not include:

- qclass;
- qtype or proof purpose;
- current client view;
- ECS, client IP, client name, or request client ID;
- conditional-forwarding branch;
- effective upstream group;
- proof source zone;
- parent zone;
- trust-anchor path;
- validation policy or algorithm set.

This allows one response path or proof purpose to seed a DNSSEC status for another path.

### 4. Unsigned NSEC/NSEC3 presence is treated as authenticated DS absence

`resolver/dnssec/validator.go:655-667` queries DS records when an RRset has no matching RRSIG. If no DS records are extracted, it calls `handleNoDSRecords`.

`resolver/dnssec/validator.go:682-690` then does:

```go
hasNSEC := len(extractNSECRecords(dsResponse.Ns)) > 0
hasNSEC3 := len(extractNSEC3Records(dsResponse.Ns)) > 0

if hasNSEC || hasNSEC3 {
    result := ValidationResultInsecure
    v.setCachedValidation(domain, result)
    return result
}
```

This code does not validate the NSEC/NSEC3 RRset signature and does not validate the parent zone chain before trusting the denial proof. The comment calls this an authenticated denial of DS existence, but the code only checks for record presence.

### 5. DNSSEC auxiliary queries do not preserve original request context

`resolver/dnssec_resolver.go:47-52` creates the validator with `upstream` as the resolver used for DS/DNSKEY lookups. `resolver/dnssec/query.go:57-69` builds synthetic requests containing only qname/qtype and sends them to `v.upstream.Resolve`.

Those synthetic requests do not preserve the original request's client IP, client names, ECS data, request client ID, or conditional-forwarding context. `resolver/upstream_tree_resolver.go:123-162` chooses upstream groups based on client metadata; missing metadata can cause DNSSEC auxiliary queries to use a different upstream view from the answer being validated.

This is a scope problem even apart from the direct basic bypass.

## Reproduction

### Environment

- Repository: `/home/hurrison/workspace/dnssec/repos/blocky`
- Commit: `e0ea9b3ea56e3d074569abd3010251e7c6ebd593`
- No root privileges required.
- No public DNS dependency; PoCs use local loopback high ports.
- Both PoCs query Blocky's real DNS listener through UDP.

### PoC 1: basic unsigned-response DNSSEC bypass

Run:

```sh
cd /home/hurrison/workspace/dnssec/repos/blocky
go run ./exp/external-dnssec-basic-bypass
```

Artifact:

```text
report/artifacts/basic-bypass-output.txt
```

Key output:

```text
query 1:
  rcode: NOERROR
  answers: cloudflare.com. A 203.0.113.77 ttl=120
  target A upstream queries: 1
  target DS upstream queries: 0
  target DNSKEY upstream queries: 0

stopping malicious upstream before query 2
query 2:
  rcode: NOERROR
  answers: cloudflare.com. A 203.0.113.77 ttl=120
  target A upstream queries: 1
  target DS upstream queries: 0
  target DNSKEY upstream queries: 0

BASIC BYPASS CONFIRMED: Blocky accepted and cached an unsigned poisoned response without querying DS/DNSKEY for the target.
```

Interpretation:

- `cloudflare.com.` is treated as if it were insecure only because the forged response contained no RRSIG records.
- Blocky does not query DS or DNSKEY for the target before accepting the answer.
- The second answer is served after the malicious upstream is shut down, proving cache replay.

### PoC 2: forged insecure proof and validation-cache scope pollution

Run:

```sh
cd /home/hurrison/workspace/dnssec/repos/blocky
go run ./exp/external-dnssec-cache-scope-pollution
```

Artifact:

```text
report/artifacts/poc-output.txt
```

Key output:

```text
query 1:
  rcode: NOERROR
  answers: victim.signed.example. A 203.0.113.66 ttl=120 | decoy.victim.signed.example. RRSIG type-covered=TXT ttl=120
  victim A upstream queries: 1
  victim DS proof queries: 1

stopping malicious upstream before query 2
query 2:
  rcode: NOERROR
  answers: victim.signed.example. A 203.0.113.66 ttl=119 | decoy.victim.signed.example. RRSIG type-covered=TXT ttl=119
  victim A upstream queries: 1
  victim DS proof queries: 1

EXP SUCCESS: poisoned data was accepted over Blocky's DNS listener and replayed on a second external query after the malicious upstream was shut down.
```

Interpretation:

- The response contains an unrelated RRSIG to force the RRset-validation path.
- The A RRset has no matching RRSIG.
- The forged DS response contains no DS and an unsigned NSEC in authority.
- Blocky caches `Insecure` for the domain and returns the poisoned answer.
- The second response is served after the malicious upstream is shut down.

## Expected behavior

For a DNSSEC validating resolver:

- Missing RRSIGs in a positive response must not automatically imply an insecure zone.
- The resolver must prove that the queried name is under an insecure delegation before accepting an unsigned answer.
- If the parent chain indicates the name should be signed, an unsigned positive answer must be treated as bogus.
- DS absence must be proven by authenticated denial of existence, not by the mere presence of NSEC/NSEC3 records.
- DNS response cache entries must not be written before the final DNSSEC decision, or they must be bound to validation metadata that is checked on cache hit.
- Validation cache entries must be scoped to the proof purpose, class, view, upstream group, proof source, and trust path.

## Actual behavior

- Unsigned positive responses are classified as `Insecure` without DS/DNSKEY chain checks.
- `CachingResolver` writes responses before outer DNSSEC validation runs.
- An unsigned NSEC/NSEC3 in a DS response can mark a domain as `Insecure`.
- The `Insecure` result is cached by bare domain name.
- Poisoned answers are replayed from Blocky's DNS cache on later external queries.

## Impact

The impact is DNSSEC validation bypass and persistent DNS cache poisoning:

- forged A/AAAA/CNAME/MX/TXT records can be returned for signed domains;
- poisoned records can be replayed to later clients for the cache TTL;
- traffic can be redirected to attacker-controlled infrastructure;
- update systems, package mirrors, service discovery, mail routing, and TLS bootstrapping flows may be affected depending on client behavior;
- split-horizon and conditional-forwarding deployments may suffer cross-view validation-state pollution;
- an attacker can also induce false `Bogus` or `Indeterminate` states in related logic, causing targeted SERVFAIL or AD-bit stripping.

The basic bypass is sufficient for a malicious or intercepted recursive upstream to defeat Blocky's documented DNSSEC protection. The cache-scope pollution path shows additional design risk in deployments with multiple views, upstream groups, or conditional forwarding.

## Attachments

[blocky-dnssec-validation-cache-scope-pollution-attachments.zip](https://github.com/user-attachments/files/28940249/blocky-dnssec-validation-cache-scope-pollution-attachments.zip)

```text
report/
  blocky-dnssec-validation-cache-scope-pollution-report.md
  attachments/
    external-dnssec-basic-bypass/
      main.go
      README.md
    external-dnssec-cache-scope-pollution/
      main.go
      README.md
  artifacts/
    basic-bypass-output.txt
    poc-output.txt
```

Attachment descriptions:

- `attachments/external-dnssec-basic-bypass/main.go`: external PoC for the direct unsigned-response DNSSEC bypass.
- `attachments/external-dnssec-basic-bypass/README.md`: usage notes for the basic bypass PoC.
- `attachments/external-dnssec-cache-scope-pollution/main.go`: external PoC for forged insecure proof and validation-cache scope pollution.
- `attachments/external-dnssec-cache-scope-pollution/README.md`: usage notes for the cache-scope PoC.
- `artifacts/basic-bypass-output.txt`: recorded output for PoC 1.
- `artifacts/poc-output.txt`: recorded output for PoC 2.

## Credit

[Yuheng Zhang @ Tsinghua University](mailto:zhangyuh25@mails.tsinghua.edu.cn)
[Jianjun Chen@ Tsinghua University](mailto:jianjun@tsinghua.edu.cn)

## References
- https://github.com/0xERR0R/blocky/security/advisories/GHSA-x845-2f78-7v36
- https://github.com/0xERR0R/blocky
