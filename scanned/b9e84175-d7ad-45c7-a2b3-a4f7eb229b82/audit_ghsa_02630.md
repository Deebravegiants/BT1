# [M] Improper Handling of Missing Values in kaml

## Summary
Severity: Medium
Advisory: GHSA-fmm9-3gv8-58f4
CVE: CVE-2021-39194
CWE: CWE-230, CWE-835
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2021-09-07
Source: https://github.com/advisories/GHSA-fmm9-3gv8-58f4
Type: github-advisory

## Affected
- Maven: `com.charleskorn.kaml:kaml` — affected >=0 <0.35.3

## Details
### Impact
Attackers that could provide arbitrary YAML input to an application that uses kaml could cause the application to endlessly loop while parsing the input. This could result in resource starvation and denial of service. 

This only affects applications that use polymorphic serialization with the default tagged polymorphism style. Applications using the property polymorphism style are not affected.

YAML input for a polymorphic type that provided a tag but no value for the object would trigger the issue, for example:

```yaml
!<x>
```

The following is a sample application that demonstrates this issue:

```kotlin
import com.charleskorn.kaml.Yaml
import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable

@Serializable
private sealed class K {
    @Serializable
    @SerialName("x")
    data class X(
        val property: String? = null,
    ) : K()
}

const val s = """
!<x>
"""

fun main() {
    println("Started.")
    val result = Yaml.default.decodeFromString(K.serializer(), s)
    println("Finished, result is $result")
}
```

On vulnerable versions of kaml, the `decodeFromString()` operation hangs and never returns. 


### Patches
Version 0.35.3 or later contain the fix for this issue.

## References
- https://github.com/charleskorn/kaml/security/advisories/GHSA-fmm9-3gv8-58f4
- https://nvd.nist.gov/vuln/detail/CVE-2021-39194
- https://github.com/charleskorn/kaml/issues/179
- https://github.com/charleskorn/kaml/commit/e18785d043fc6324c81e968aae9764b4b060bc6a
- https://github.com/charleskorn/kaml
