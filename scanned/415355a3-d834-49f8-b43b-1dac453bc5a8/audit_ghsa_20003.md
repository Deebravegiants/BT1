# [H] Apiman Vert.x Gateway has Transitive Hazelcast connection caching issue

## Summary
Severity: High
Advisory: GHSA-q2fj-6h62-59m2
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-12-30
Source: https://github.com/advisories/GHSA-q2fj-6h62-59m2
Type: github-advisory

## Affected
- Maven: `io.apiman:apiman-gateway-platforms-vertx` — affected >=0 <3.0.0.Final
- Maven: `io.apiman:apiman-distro-vertx` — affected >=0 <3.0.0.Final

## Details
### Impact

If you are using the **Apiman Vert.x Gateway** prior to Apiman 3.0.0.Final, a connection caching issue in Hazelcast could allow an unauthenticated, remote attacker to access and manipulate data in the cluster with another authenticated connection's identity.

Hazelcast is a transitive dependency of the Apiman Vert.x Gateway.

The precise risk is difficult to quantify at this juncture as plugins deployed by users may make use of Hazelcast in a different manner to the main Apiman codebase.

If any of your custom Apiman plugins specify Hazelcast dependencies, you should also bump these versions. 

Hint: an easy way to track Apiman dependency versions is to use `apiman-parent`.

If you use the Apiman Tomcat or WildFly Gateway this does not affect you.

### Patches

Upgrade to **Apiman 3.0.0.Final or later**.

If you are using an older version of Apiman and need to remain on that version, contact to your Apiman support provider for advice/long-term support.

### Workarounds

None (other than doing your own build).

### References

* https://github.com/advisories/GHSA-c5hg-mr8r-f6jp

## References
- https://github.com/apiman/apiman/security/advisories/GHSA-q2fj-6h62-59m2
- https://github.com/advisories/GHSA-c5hg-mr8r-f6jp
- https://github.com/apiman/apiman
- https://support.hazelcast.com/s/article/Security-Advisory-for-CVE-2022-36437
