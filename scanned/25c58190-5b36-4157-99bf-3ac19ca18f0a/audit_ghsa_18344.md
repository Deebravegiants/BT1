# [M] Openfire has potential identity spoofing issue via unsafe CN parsing

## Summary
Severity: Medium
Advisory: GHSA-w252-645g-87mp
CVE: CVE-2025-59154
CWE: CWE-290
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-09-16
Source: https://github.com/advisories/GHSA-w252-645g-87mp
Type: github-advisory

## Affected
- Maven: `org.igniterealtime.openfire:xmppserver` — affected >=0 <5.0.2

## Details
## Summary

Identity spoofing in X.509 client certificate authentication in Openfire allows internal attackers to impersonate other users via crafted certificate subject attributes, due to regex-based extraction of CN from an unescaped, provider-dependent DN string.

## Analysis

Openfire’s SASL EXTERNAL mechanism for client TLS authentication contains a vulnerability in how it extracts user identities from X.509 certificates. Instead of parsing the structured ASN.1 data, the code calls `X509Certificate.getSubjectDN().getName()` and applies a regex to look for `CN=`. This method produces a provider-dependent string that does not escape special characters. In SunJSSE (`sun.security.x509.X500Name`), for example, commas and equals signs inside attribute values are not escaped.

As a result, a malicious certificate can embed `CN=` inside another attribute value (e.g. `OU="CN=admin,"`). The regex will incorrectly interpret this as a legitimate Common Name and extract admin. If SASL EXTERNAL is enabled and configured to map CNs to user accounts, this allows the attacker to impersonate another user.

## Impact

When there is no explicit configuration override, Openfire defaults to using certificate attributes as follows:

- Server-to-server certificates: first the Subject Alternative Name (SAN), and if that is not available, the Common Name (CN).
- Client-to-server certificates: only the Common Name (CN).

Use of CN for identity mapping was phased out by the CA/Browser Forum. CAB Forum-compliant CAs no longer allow arbitrary Subject RDNs and always include SANs. As a result, certificates issued by public CAs for use on the open Internet are unlikely to be exploitable, though older certificates still within their validity period could theoretically be abused.

The primary risks exist in private CA environments and client certificate authentication, where identity mapping may rely solely on the CN. Both of these are niche deployment scenarios.

## Patches

The path has been prepared by replacing the use of `getSubjectDN().getName()` with standards-compliant `LdapName` parsing of the RFC2253 representation of `X500Principal`. This avoids unescaped provider-dependent strings and prevents regex from matching malicious substrings.  

The fix is included in Openfire 5.0.2 and 5.1.0. Users should upgrade to this version as soon as it becomes available.  

Starting in Openfire 5.0.2, Openfire will by default prefer a Subject Alternative Name-based identity over a Common Name based one for client-to-server authentication (issue OF-3123). For server-to-server authentication, this already is the case.

In Openfire 5.1.0, Openfire will no longer, by default, use Common Name based identities, although this functionality can be restored through configuration changes (issue OF-3122).
 
## Workarounds

The vulnerability is fixed in the upcoming release, but there are operational mitigations you can apply today.

### Full workaround (drop-in replacement JAR using the fixed mapper)
 _This is a complete workaround:_
1. Take the fixed mapper implementation (the code that uses LdapName / RFC2253 parsing) from the patched Openfire source.
2. Create a new Java class in your proprietary namespace (for example `com.acme.openfire.SafeCNCertificateIdentityMapping`) that implements the same Openfire certificate-identity mapping interface and contains the fixed parsing logic. Ensure the logic exactly mirrors the patched behavior (use `X500Principal.getName()` with RFC2253 and `javax.naming.ldap.LdapName` to parse RDNs, do not rely on `getSubjectDN().getName()` or provider-dependent strings).
3. Package the class into a JAR file.
4. Place the JAR into Openfire’s lib/ directory (e.g. `$OPENFIRE_HOME/lib/your-fixed-mapper.jar`).
5. Configure Openfire to use your class for mapping by setting the following properties (in the admin console / system properties). Note that it remains advisable to configure Openfire to keep preferring SAN-based identities:
```
# For server-to-server identity mapping
provider.serverCertIdentityMap.classList=org.jivesoftware.util.cert.SANCertificateIdentityMapping,com.acme.openfire.SafeCNCertificateIdentityMapping

# For client-to-server identity mapping
provider.clientCertIdentityMap.classList=org.jivesoftware.util.cert.SANCertificateIdentityMapping,com.acme.openfire.SafeCNCertificateIdentityMapping
```
Both properties accept a comma-separated list of fully-qualified class names; listing only your safe mapper forces Openfire to use your implementation instead of the vulnerable built-in mapper. After placing the JAR and updating properties, *restart Openfire*.

**Notes & caveats for the full workaround**

- This is effectively a complete mitigation for the vulnerable CN-extraction behavior without deploying a new official release.
- Maintain the JAR: you are responsible for keeping the custom class updated if you upgrade Openfire to newer major versions.
- Ensure your custom mapper truly implements the patched parsing (do not copy the vulnerable `getSubjectDN().getName()` + regex approach). Use `X500Principal` → `getName(RFC2253)` → `new LdapName(...)` → iterate RDNs in a robust way.
- Because this runs in the Openfire JVM, follow your organization’s binary-signing and review policies before deploying.

### Other, lesser workarounds

#### Use SAN-only mapping
Configure the mapper list to only include Openfire’s SAN mapper: `org.jivesoftware.util.cert.SANCertificateIdentityMapping`. This prevents CN parsing-based spoofing but breaks authentication for certificates that contain only a CN and no SAN.

#### Disable certificate-based authentication:
- For server-to-server, disabling certificate auth leaves only Server Dialback, which is less secure; depending on your environment, this may be a worse trade-off.
- For client-to-server, disable “mutual authentication” in the admin console to stop client cert authentication altogether.

## References

- Openfire issue tracker: [OF-3124: Potential identity spoofing via unsafe CN parsing](https://igniterealtime.atlassian.net/browse/OF-3124)
- Affected code: [CNCertificateIdentityMapping.java#L43](https://github.com/igniterealtime/Openfire/blob/8d073dda36905da0fdee7cb623c025a01a5cbf6b/xmppserver/src/main/java/org/jivesoftware/util/cert/CNCertificateIdentityMapping.java#L43)  
- Openfire issue tracker: [OF-3122: Stop by default using Common Name based identities](https://igniterealtime.atlassian.net/browse/OF-3122)
- Openfire issue tracker: [OF-3123: For client mutual authentication, prefer Subject Alternative Name for identities](https://igniterealtime.atlassian.net/browse/OF-3123)

## References
- https://github.com/igniterealtime/Openfire/security/advisories/GHSA-w252-645g-87mp
- https://nvd.nist.gov/vuln/detail/CVE-2025-59154
- https://github.com/igniterealtime/Openfire
- https://github.com/igniterealtime/Openfire/blob/8d073dda36905da0fdee7cb623c025a01a5cbf6b/xmppserver/src/main/java/org/jivesoftware/util/cert/CNCertificateIdentityMapping.java#L43
- https://igniterealtime.atlassian.net/browse/OF-3122
- https://igniterealtime.atlassian.net/browse/OF-3123
- https://igniterealtime.atlassian.net/browse/OF-3124
