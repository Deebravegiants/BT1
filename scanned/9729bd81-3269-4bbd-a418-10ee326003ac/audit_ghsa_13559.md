# [H] Directus crashes on invalid WebSocket message

## Summary
Severity: High
Advisory: GHSA-hmgw-9jrg-hf2m
CVE: CVE-2023-45820
CWE: CWE-755
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-hmgw-9jrg-hf2m
Type: github-advisory

## Affected
- npm: `directus` — affected >=10.4.0 <10.6.2

## Details
### Summary
It seems that any Directus installation that has websockets enabled can be crashed if the websocket server receives an invalid frame. This could probably be posted as an issue and I might even be able to put together a pull request for a fix (if only I had some extra time...), but I decided to instead post as a vulnerability just for the maintainers, since this seemingly can be used to crash any live Directus server if websockets are enabled, so public disclosure is not a good idea until the issue is fixed.

### Details
The fix for this seems quite simple; the websocket server just needs to properly catch the error instead of crashing the server. See for example: https://github.com/websockets/ws/issues/2098

### PoC
- Start a fresh Directus server (using for example the compose file here: https://docs.directus.io/self-hosted/docker-guide.html). Enable websockets by setting `WEBSOCKETS_ENABLED: 'true'` environment variable.
- run a separate node app somewhere else to send an invalid frame to the server:

```
const WebSocket = require("ws");
const websocket = new WebSocket("ws://0.0.0.0:8055/websocket");
websocket.on("open", function () {
  const chunk = Buffer.from("a180", "hex");
  websocket._socket.write(chunk);
});
```

### Impact
The server crashes with an error: `RangeError: Invalid WebSocket frame: RSV2 and RSV3 must be clear`. Server needs to be manually restarted to get back online (if there's no recovery mechanism in place, as there often isn't with simple node servers). This was confirmed on a local server, and additionally I was able to crash our staging server with the same code, just pointing to our staging Directus server running at fly.io. It seems to also crash servers running in the [directus.cloud](https://directus.cloud) service. I created https://websocket-test.directus.app/, pointed the above script to the websocket url of that instance and the server does crash for a while. It seems that in there there's a mechanism for bringing the server back up quite fast, but it would be quite trivial for anyone to DoS any server running in directus.cloud by just spamming these invalid frames to the server.

## References
- https://github.com/directus/directus/security/advisories/GHSA-hmgw-9jrg-hf2m
- https://nvd.nist.gov/vuln/detail/CVE-2023-45820
- https://github.com/directus/directus/commit/243eed781b42d6b4948ddb8c3792bcf5b44f55bb
- https://github.com/directus/directus
- https://github.com/directus/directus/releases/tag/v10.6.2
