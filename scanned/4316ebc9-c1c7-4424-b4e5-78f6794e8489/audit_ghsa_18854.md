# [C] Akka.Remote TLS did not properly implement certificate-based authentication

## Summary
Severity: Critical
Advisory: GHSA-jhpv-4q4f-43g5
CVE: CVE-2025-61778
CWE: CWE-290
Ecosystem: NuGet
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-10-07
Source: https://github.com/advisories/GHSA-jhpv-4q4f-43g5
Type: github-advisory

## Affected
- NuGet: `Akka.Remote` — affected >=1.2.0 <1.5.52
- NuGet: `Akka.Cluster` — affected >=1.2.0 <1.5.52

## Details
### Impact

This is a critical network security vulnerability for Akka.Remote **users who have SSL / TLS enabled** on their Akka.Remote connections and were expecting certificate-based authentication to be enforced on all peers attempting to join the network.

In all versions of Akka.Remote from v1.2.0 to v1.5.51, TLS could be enabled via our `akka.remote.dot-netty.tcp` transport and this would correctly enforce private key validation on the server-side of inbound connections. Akka.Remote, however, never asked the outbound-connecting client to present ITS certificate - therefore it's possible for untrusted parties to connect to a private key'd Akka.NET cluster and begin communicating with it **without any certificate**. 

The issue here is that for certificate-based authentication to work properly, ensuring that all members of the Akka.Remote network are secured with the same private key, Akka.Remote needed to implement mutual TLS. This was not the case before Akka.NET v1.5.52.

If you are running Akka.NET inside a private network you fully control or you were never using TLS in the first place, then this bug has no impact on you. However: if you are using TLS to secure your network YOU MUST upgrade to Akka.NET V1.5.52 or later.

### Patches

https://github.com/akkadotnet/akka.net/pull/7847 - forces "fail fast" semantics if TLS is enabled but the private key is missing or invalid. Previous versions would only check that once connection attempts occurred.
https://github.com/akkadotnet/akka.net/pull/7851 - **critical fix**: enforces mutual TLS (mTLS) by default, so both parties must be keyed using the same certificate. This fulfills the original security 

These updates have been shipped into Akka.NET v1.5.52: https://github.com/akkadotnet/akka.net/releases/tag/1.5.52

### Workarounds

If your application isn't exposed publicly, then CVE-2025-61778 has no practical impact on your application. That being said: upgrading to Akka.NET v1.5.52 or later is a good idea.

### References

Please view our latest network security documentation here: https://getakka.net/articles/remoting/security.html

## References
- https://github.com/akkadotnet/akka.net/security/advisories/GHSA-jhpv-4q4f-43g5
- https://nvd.nist.gov/vuln/detail/CVE-2025-61778
- https://github.com/akkadotnet/akka.net/pull/7847
- https://github.com/akkadotnet/akka.net/pull/7851
- https://getakka.net/articles/remoting/security.html
- https://github.com/akkadotnet/akka.net
- https://github.com/akkadotnet/akka.net/releases/tag/1.5.52
