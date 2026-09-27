# [H] jackson-databind has a PolymorphicTypeValidator bypass via generic type parameters that allows arbitrary class instantiation

## Summary
Severity: High
Advisory: GHSA-j3rv-43j4-c7qm
CVE: CVE-2026-54512
CWE: CWE-184, CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-j3rv-43j4-c7qm
Type: github-advisory

## Affected
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.10.0 <2.18.8
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4
- Maven: `com.fasterxml.jackson.core:jackson-databind` — affected >=2.19.0 <2.21.4
- Maven: `tools.jackson.core:jackson-databind` — affected >=3.0.0 <3.1.4

## Details
`jackson-databind`'s `PolymorphicTypeValidator` (PTV) is the primary safety mechanism guarding polymorphic deserialization. When polymorphic typing is enabled and a type identifier contains generic parameters (i.e. the type ID string contains `<`), `DatabindContext._resolveAndValidateGeneric()` validates **only the raw container class name** (the substring before `<`) against the configured PTV.

If the container type is approved, the method parses the full canonical type string via `TypeFactory.constructFromCanonical()` and returns the fully parameterized type **without ever validating the nested type arguments** against the PTV. The nested type arguments are then resolved, instantiated, and populated as beans during deserialization.

An attacker who controls the type ID can therefore place a denied class as a generic type parameter of an allowed container — for example `java.util.ArrayList<com.evil.Gadget>` when only `java.util.ArrayList` is allow-listed. The container passes the PTV check; `com.evil.Gadget` is loaded via `Class.forName(name, true, loader)`, instantiated, and its properties are set from attacker-controlled JSON. This completely bypasses an explicitly configured PTV allow-list.

This is the same vulnerability class responsible for the historical sequence of jackson-databind deserialization CVEs; here it manifests as a validator bypass rather than a missing deny-list entry.


## Impact

- **Bypass of the PTV allow-list**, including the recommended `BasicPolymorphicTypeValidator` configured with name-prefix allow rules.
- **Arbitrary class instantiation** of any type assignable to the container's element/parameter position, with attacker-controlled property values (setter/field injection).
- **Potential unauthenticated remote code execution** when a class with exploitable side effects (JNDI lookup, JDBC/connection-pool gadgets,`TemplatesImpl`-style loaders, etc.) is present on the classpath.

Applications that accept untrusted JSON and rely on a configured PTV — the documented, security-conscious configuration — are affected.


## Proof of Concept

Configuration restricting polymorphic deserialization to a single safe container:

```java
BasicPolymorphicTypeValidator ptv = BasicPolymorphicTypeValidator.builder()
        .allowIfSubType("java.util.ArrayList")
        .build();

ObjectMapper mapper = JsonMapper.builder()
        .polymorphicTypeValidator(ptv)
        .build();
```

Malicious payload (`Wrapper.value` is `Object` with `@JsonTypeInfo(use = Id.CLASS, include = As.WRAPPER_ARRAY)`):

```json
{"value":["java.util.ArrayList<com.evil.EvilGadget>",[{"cmd":"calc.exe"}]]}
```

On vulnerable versions, `com.evil.EvilGadget` is instantiated and its `cmd` property is set, despite only `java.util.ArrayList` being allow-listed. On `2.18.8` / `2.21.4` / `3.1.4` the deserialization throws `InvalidTypeIdException` before instantiation.

**Variant payloads** (all bypass an `ArrayList`/`HashMap` allow-list):

| Type ID | Smuggled type position |
|---|---|
| `java.util.ArrayList<Evil>` | list element |
| `java.util.HashMap<Evil,String>` | map key |
| `java.util.HashMap<String,Evil>` | map value |
| `java.util.ArrayList<java.util.ArrayList<Evil>>` | nested element |
| `java.util.ArrayList<Evil[]>` | array element |

---

## Patches

Fixed in **2.18.8**, **2.21.4** and **3.1.4** via the changes for [FasterXML/jackson-databind#5988](https://github.com/FasterXML/jackson-databind/issues/5988), commit `434d6c511`. The fix adds recursive validation of each non-trivial type parameter (and array element types appearing as parameters) through the full PTV chain, with documented exemptions for `Object` (wildcard resolution) and `Enum` types.

`PolymorphicTypeValidator` was added in 2.10.0 so vulnerability N/A for versions prior to that.

## References
- https://github.com/FasterXML/jackson-databind/security/advisories/GHSA-j3rv-43j4-c7qm
- https://nvd.nist.gov/vuln/detail/CVE-2026-54512
- https://github.com/FasterXML/jackson-databind/issues/5988
- https://github.com/FasterXML/jackson-databind/commit/434d6c511de7fdd9872f29157aafb6162d12d8d5
- https://github.com/FasterXML/jackson-databind
