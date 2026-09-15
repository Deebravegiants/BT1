# [M] jackson-databind omits java.lang.Comparable from DefaultBaseTypeLimitingValidator's unsafe base types

## Summary
Severity: Medium
Advisory: CVE-2026-83557
Aliases: GHSA-gx83-3vf8-gh7j
CVSS: 5.6 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-09-01
Source: https://osv.dev/vulnerability/CVE-2026-83557
Type: osv

## Details
DefaultBaseTypeLimitingValidator is the PolymorphicTypeValidator applied automatically whenever @JsonTypeInfo is used without an explicitly configured custom validator. It denies polymorphic resolution only for a fixed set of "unsafe base types", and its isSafeSubType method returns true unconditionally for every base type outside that set. java.lang.Comparable was absent from the list despite being implemented by a very large fraction of JDK and application classes, comparable in breadth to java.io.Serializable, which is on the list for that reason. An application declaring an @JsonTypeInfo-annotated property or class with Comparable as its base type, and no custom PolymorphicTypeValidator, will accept a type identifier for essentially any class implementing Comparable. This yields an attacker-controlled object instantiation primitive; a demonstrated case constructs a java.io.File for an arbitrary attacker-chosen path, which becomes path-traversal-adjacent if the application subsequently calls path-sensitive methods on the value. No class implementing Comparable has been identified that yields code execution through deserialization alone. Global Default Typing via activateDefaultTyping is not affected, because that method structurally requires an explicit PolymorphicTypeValidator argument. This affects com.fasterxml.jackson.core:jackson-databind from 2.11.0 before 2.18.10, from 2.19.0 before 2.21.6, and from 2.22.0 before 2.22.2, and tools.jackson.core:jackson-databind from 3.0.0 before 3.1.6 and from 3.2.0 before 3.2.2. Users should upgrade to 2.18.10, 2.21.6, 2.22.2, 3.1.6, or 3.2.2.

## References
- https://repo.maven.apache.org/maven2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/83xxx/CVE-2026-83557.json
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-gx83-3vf8-gh7j
- https://nvd.nist.gov/vuln/detail/CVE-2026-83557
- https://github.com/FasterXML/jackson-databind/issues/6156
- https://github.com/FasterXML/jackson-databind/commit/eb3b7fc0f9c0d27f471550ac3316b17d1987388f
- https://github.com/FasterXML/jackson-databind/pull/6155
- https://github.com/FasterXML/jackson-databind
