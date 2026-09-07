# [M] path traversal in Jooby

## Summary
Severity: Medium
Advisory: GHSA-px9h-x66r-8mpc
CVE: CVE-2020-7647
CWE: CWE-22
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2020-05-13
Source: https://github.com/advisories/GHSA-px9h-x66r-8mpc
Type: github-advisory

## Affected
- Maven: `io.jooby:jooby` — affected >=0 <2.8.2
- Maven: `org.jooby:jooby` — affected >=0 <2.8.2

## Details
### Impact
Access to sensitive information available from classpath. 

### Patches
Patched version: 1.6.7 and 2.8.2

Commit 1.x: https://github.com/jooby-project/jooby/commit/34f526028e6cd0652125baa33936ffb6a8a4a009

Commit 2.x: https://github.com/jooby-project/jooby/commit/c81479de67036993f406ccdec23990b44b0bec32

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_

### References

Latest 1.x version: 1.6.6

#### Arbitrary class path resource access 1
When sharing a *File System* directory as in:

``` java
assets("/static/**", Paths.get("static"));
```

The class path is also searched for the file (`org.jooby.handlers.AssetHandler.loader`):
[jooby/AssetHandler.java at 1.x · jooby-project/jooby · GitHub](https://github.com/jooby-project/jooby/blob/1.x/jooby/src/main/java/org/jooby/handlers/AssetHandler.java)

``` java
  private static Loader loader(final Path basedir, final ClassLoader classloader) {
    if (Files.exists(basedir)) {
      return name -> {
        Path path = basedir.resolve(name).normalize();
        if (Files.exists(path) && path.startsWith(basedir)) {
          try {
            return path.toUri().toURL();
          } catch (MalformedURLException x) {
            // shh
          }
        }
        return classloader.getResource(name);
      };
    }
    return classloader::getResource;
  }
```

If we send `/static/WEB-INF/web.xml` it will fail to load it from the file system but will go into `classloader.getResource(name)` where name equals `/WEB-INF/web.xml` so will succeed and return the requested file. This way we can get any configuration file or even the application class files

If assets are configured for a certain extension we can still bypass it. eg:

```java
assets("/static/**/*.js", Paths.get("static"));
```

We can send:

```
http://localhost:8080/static/io/yiss/App.class.js
```

#### Arbitrary class path resource access 2
This vulnerability also affects assets configured to access resources from the root of the class path. eg:

```java
assets("/static/**");
```

In this case we can traverse `static` by sending:

```
http://localhost:8080/static/..%252fio/yiss/App.class
```

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [jooby](https://github.com/jooby-project/jooby/issues)
* Email us at [support@jooby.io](mailto:support@jooby.io)

## References
- https://github.com/jooby-project/jooby/security/advisories/GHSA-px9h-x66r-8mpc
- https://nvd.nist.gov/vuln/detail/CVE-2020-7647
- https://github.com/jooby-project/jooby/commit/34f526028e6cd0652125baa33936ffb6a8a4a009
- https://github.com/jooby-project/jooby
- https://snyk.io/vuln/SNYK-JAVA-IOJOOBY-568806
- https://snyk.io/vuln/SNYK-JAVA-IOJOOBY-568806,
- https://snyk.io/vuln/SNYK-JAVA-ORGJOOBY-568807
- https://snyk.io/vuln/SNYK-JAVA-ORGJOOBY-568807,
