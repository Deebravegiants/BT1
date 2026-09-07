# [C] Remote Code Execution Vulnerability in Session Storage

## Summary
Severity: Critical
Advisory: GHSA-hc33-32vw-rpp9
CVE: CVE-2021-29485
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2021-07-01
Source: https://github.com/advisories/GHSA-hc33-32vw-rpp9
Type: github-advisory

## Affected
- Maven: `io.ratpack:ratpack-core` — affected >=0 <1.9.0

## Details
### Impact

A malicious attacker can achieve Remote Code Execution (RCE) via a maliciously crafted Java deserialization gadget chain leveraged against the Ratpack session store.

If your application does not use Ratpack's session mechanism, it is not vulnerable.

### Details

Attackers with the ability to write to session data, can potentially craft payloads that deserialize unsafe objects, leading to the ability to remotely execute arbitrary code. 
This is known as an “[insecure deserialization](https://portswigger.net/web-security/deserialization)” vulnerability, or “gadget vulnerability”.

Ratpack allows session data to be stored server side in an external system such as a relational database, or client side via user cookies.
When using server side storage, the attacker would need to obtain the ability to write to the session data store.
When using client side storage, the attacker would need to obtain the secrets used to encrypt and/or sign the session data stored in user cookies.

Ratpack's session mechanism allows storing serialized objects, of arbitrary types. 
The type must be specified when writing the data and when reading, with data only deserialized when there is an exact type match.
However, in the process of deserializing an object of a known/trusted/deserialization-safe type, it may attempt to deserialize unsafe types.

By default Ratpack uses Java's built-in serialization mechanism, though other serialization providers can be used.
The exact types of payloads required to enable an exploit depend on the exact serialization mechanism used.

To mitigate this vulnerability, Ratpack now employs a “strict allow-list” when deserializing (and serializing) objects to session data. 
All concrete types of objects serialized must be explicitly declared as safe.
Some standard well known JDK types are registered by default.

Serialization is provided by implementations of [`SessionSerializer`](https://ratpack.io/manual/1.9.0/api/ratpack/session/SessionSerializer.html).
Its existing methods have been deprecated, and replaced with a [new methods](https://ratpack.io/manual/1.9.0/api/ratpack/session/SessionSerializer.html#deserialize(java.lang.Class,java.io.InputStream,ratpack.session.SessionTypeFilter)) that accept a [`SessionTypeFilter`](https://ratpack.io/manual/1.9.0/api/ratpack/session/SessionTypeFilter.html) that can be used to assert whether a type is allowed when serializing and deserializing.

The default serializer implementation has been updated to use this mechanism.
Any proprietary implementations should also be updated to consult the type filter _before_ serializing or deserializing data.
Warnings will be logged any time an implementation that does not implement the new methods is used.

Upon upgrading to Ratpack 1.9, users of the built-in serialization mechanism will need to change their application to declare all types currently being serialized as being safe. This can be done using the new [`SessionModule.allowTypes()`](https://ratpack.io/manual/1.9.0/api/ratpack/session/SessionModule.html#allowTypes(com.google.inject.Binder,java.lang.Class...)) method. Please see its documentation for details...))

### Patches

Ratpack 1.9.0 introduces a strict allow-list mechanism that mitigates this vulnerability when used.

### Workarounds

The simplest mitigation for users of earlier versions is to reduce the likelihood of attackers being able to write to the session data store. 

Alternatively or additionally, the allow-list mechanism could be manually back ported by providing an alternative implementation of `SessionSerializer` that uses an allow-list.

### References

 - https://foxglovesecurity.com/2015/11/06/what-do-weblogic-websphere-jboss-jenkins-opennms-and-your-application-have-in-common-this-vulnerability/
 - https://owasp.org/www-community/vulnerabilities/Deserialization_of_untrusted_data

## References
- https://github.com/ratpack/ratpack/security/advisories/GHSA-hc33-32vw-rpp9
- https://nvd.nist.gov/vuln/detail/CVE-2021-29485
- https://github.com/ratpack/ratpack
- https://mvnrepository.com/artifact/io.ratpack/ratpack-core
