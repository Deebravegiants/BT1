# [H] CedarJava has type confusion vulnerability 

## Summary
Severity: High
Advisory: GHSA-93g4-m6xv-cmvr
CVE: CVE-2026-55772
CWE: CWE-843
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-19
Source: https://github.com/advisories/GHSA-93g4-m6xv-cmvr
Type: github-advisory

## Affected
- Maven: `com.cedarpolicy:cedar-java` — affected >=0 <2.3.6
- Maven: `com.cedarpolicy:cedar-java` — affected >=3.1.2 <3.4.1
- Maven: `com.cedarpolicy:cedar-java` — affected >=4.0.0 <4.9.0

## Details
### Summary

CedarJava is an open source Java implementation of the Cedar policy language, used for fine-grained authorization decisions. Under certain circumstances, improper input handling could allow type confusion across the Java-Rust FFI boundary.

### Impact

**Record-to-Entity type confusion across the Java-Rust FFI boundary**

CedarJava sends authorization requests to the Rust cedar-policy evaluator as JSON. The JSON protocol reserves magic single-key object shapes (`__entity` and `__extn`) for entity references and extension values. When serializing a `CedarMap`, there is no validation preventing these reserved keys from being used. If an integrating service builds a `CedarMap` from caller-supplied key/value data (such as request headers, user-defined metadata, or resource tags), an actor who controls those keys could cause the Rust evaluator to interpret a record as an entity reference.

This issue requires the integrating service to build a `CedarMap` where the an actor controls the keys, and a policy must reference that value in a when/unless clause.

### Impacted versions: 
< 4.9

### Patches
Addressed in CedarJava version 2.3.6, 3.4.1, and 4.9 and above. We recommend upgrading to the latest version and ensuring any forked or derivative code is patched to incorporate the new fixes.

### Workarounds
Enable schema-based request validation to catch type mismatches. Validate that user-controlled data does not contain reserved keys (`__entity` or `__extn`) before building `CedarMap` objects.

### References
If you have any questions or comments about this advisory, we ask that you contact us directly via email to [cedar-policy-security@lists.cncf.io](mailto:cedar-policy-security@lists.cncf.io). Please do not create a public GitHub issue.

## References
- https://github.com/cedar-policy/cedar-java/security/advisories/GHSA-93g4-m6xv-cmvr
- https://nvd.nist.gov/vuln/detail/CVE-2026-55772
- https://github.com/cedar-policy/cedar-java
