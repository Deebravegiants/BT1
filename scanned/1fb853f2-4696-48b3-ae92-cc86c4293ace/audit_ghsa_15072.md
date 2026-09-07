# [H] Ion Java StackOverflow vulnerability

## Summary
Severity: High
Advisory: GHSA-264p-99wq-f4j6
CVE: CVE-2024-21634
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-01-03
Source: https://github.com/advisories/GHSA-264p-99wq-f4j6
Type: github-advisory

## Affected
- Maven: `com.amazon.ion:ion-java` — affected >=0 <1.10.5
- Maven: `software.amazon.ion:ion-java` — affected >=0

## Details
### Impact

A potential denial-of-service issue exists in `ion-java` for applications that use `ion-java` to:

* Deserialize Ion text encoded data, or
* Deserialize Ion text or binary encoded data into the `IonValue` model and then invoke certain `IonValue` methods on that in-memory representation.

An actor could craft Ion data that, when loaded by the affected application and/or processed using the `IonValue` model, results in a `StackOverflowError` originating from the `ion-java` library.

Impacted versions: <1.10.5

### Patches

The patch is included in `ion-java` >= 1.10.5.

### Workarounds

Do not load data which originated from an untrusted source or that could have been tampered with. **Only load data you trust.**

----

If you have any questions or comments about this advisory, we ask that you contact AWS/Amazon Security via our vulnerability reporting page [1] or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

[1] https://aws.amazon.com/security/vulnerability-reporting

## References
- https://github.com/amazon-ion/ion-java/security/advisories/GHSA-264p-99wq-f4j6
- https://nvd.nist.gov/vuln/detail/CVE-2024-21634
- https://github.com/amazon-ion/ion-java
- https://security.netapp.com/advisory/ntap-20241108-0002
