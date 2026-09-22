# [H] Class Loading Vulnerability in Artemis

## Summary
Severity: High
Advisory: GHSA-227w-wv4j-67h4
CVE: CVE-2024-23682
CWE: CWE-501, CWE-653
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:R/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-227w-wv4j-67h4
Type: github-advisory

## Affected
- Maven: `de.tum.in.ase:artemis-java-test-sandbox` — affected >=0 <1.8.0

## Details
### Impact
This affects all Artemis users who test Java assignments. **Ares is not required.**
Students code that gets automatically tested can run arbitrary code in the container,
or arbitrary code on the machine of an assessor in case of manual correction.

### Patches
The problem cannot be resolved easily in Ares itself. Use the Maven Enforcer Plugin as follows:

```xml
<plugin>
    <groupId>org.apache.maven.plugins</groupId>
    <artifactId>maven-enforcer-plugin</artifactId>
    <version>3.0.0</version>
    <executions>
        <execution>
            <id>enforce-no-student-code-in-trusted-packages</id>
            <phase>process-classes</phase>
            <goals>
                <goal>enforce</goal>
            </goals>
        </execution>
    </executions>
    <configuration>
        <rules>
            <requireFilesDontExist>
                <files>
                    <!-- ADD HERE THE RULES ARES TELLS YOU ARE MISSING -->
                </files>
            </requireFilesDontExist>
        </rules>
    </configuration>
</plugin>
```

This fails the build if student classes reside in such packages that Ares trusts. Trusted packages added in Ares using `@AddTrustedPackage` should be added as well.

### For more information
If you have any questions or comments about this advisory:
* Open a discussion https://github.com/ls1intum/Ares/discussions
* Open an issue in https://github.com/ls1intum/Ares/issues
* Email us, see https://github.com/ls1intum/Ares/security/policy

### References
See the assignment of Julius that passes the tests in TUM Artemis course: "Test - Praktikum: Grundlagen der Programmierung (Testkurs für Tutoren) - Security Tests" (if that still exists in 2022).

Also see #15 for almost the same problem.

## References
- https://github.com/ls1intum/Ares/security/advisories/GHSA-227w-wv4j-67h4
- https://nvd.nist.gov/vuln/detail/CVE-2024-23682
- https://github.com/ls1intum/Ares/issues/15
- https://github.com/ls1intum/Ares
- https://github.com/ls1intum/Ares/releases/tag/1.8.0
- https://vulncheck.com/advisories/vc-advisory-GHSA-227w-wv4j-67h4
