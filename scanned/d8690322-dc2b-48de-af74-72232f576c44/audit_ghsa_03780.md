# [H] High severity vulnerability that affects generator-jhipster

## Summary
Severity: High
Advisory: GHSA-mc84-xr9p-938r
CWE: CWE-494, CWE-829
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2019-09-23
Source: https://github.com/advisories/GHSA-mc84-xr9p-938r
Type: github-advisory

## Affected
- npm: `generator-jhipster` — affected >=0 <6.3.1

## Details
## Generated code uses repository configuration that downloads over HTTP instead of HTTPS

### Impact
Gradle users were using the http://repo.spring.io/plugins-release repositories in plain HTTP, and not HTTPS, so a man-in-the-middle attack was possible at build time.

### Patches

Maven users should at least upgrade to 6.3.0 while Gradle users should update to 6.3.1.
If you are not able to upgrade make sure not to use a Maven repository via `http` in your build file.

### Workarounds

Replace all custom repository definitions in `build.gradle` or `pom.xml` with their `https` version.

e.g.

```xml
 <repository>
            <id>oss.sonatype.org-snapshot</id>
            <url>https://oss.sonatype.org/content/repositories/snapshots</url> // <-- must be httpS
            <releases>
                <enabled>false</enabled>
            </releases>
            <snapshots>
                <enabled>true</enabled>
            </snapshots>
</repository>
```

```gradle
maven { url "https://repo.spring.io/plugins-release" } // <-- must be httpS
```

### References
* https://nvd.nist.gov/vuln-metrics/cvss/v3-calculator?vector=AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H
* https://max.computer/blog/how-to-take-over-the-computer-of-any-java-or-clojure-or-scala-developer/

### For more information
If you have any questions or comments about this advisory:
* Open an issue in [https://github.com/jhipster/generator-jhipster/issues](https://github.com/jhipster/generator-jhipster/issues)

## References
- https://github.com/jhipster/generator-jhipster/security/advisories/GHSA-mc84-xr9p-938r
- https://github.com/advisories/GHSA-mc84-xr9p-938r
- https://github.com/jhipster/generator-jhipster
- https://snyk.io/vuln/SNYK-JS-GENERATORJHIPSTER-536074
