# [M] Quarkus potentially leaks data when duplicating a duplicated context

## Summary
Severity: Medium
Advisory: GHSA-9623-mj7j-p9v4
CVE: CVE-2025-49574
CWE: CWE-668
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2025-06-23
Source: https://github.com/advisories/GHSA-9623-mj7j-p9v4
Type: github-advisory

## Affected
- Maven: `io.quarkus:quarkus-vertx` — affected >=0 <3.15.6
- Maven: `io.quarkus:quarkus-vertx` — affected >=3.16.0.CR1 <3.20.2
- Maven: `io.quarkus:quarkus-vertx` — affected >=3.21.0.CR1 <3.24.1

## Details
### Impact

Vert.x 4.5.12 has changed the semantics of the duplication of duplicated context.

Duplicated context is an object used to propagate data through a processing (synchronous or asynchronous). Each "transaction" or "processing" runs on its own isolated duplicated context.

Initially, duplicating a duplicated context was creating a fresh (empty) new context, meaning that the new duplicated context can be used to managed a separated transaction.

In Vert.x 4.5.12, this semantics has changed, and since the content of the parent duplicated context is copied into the new one, potentially leaking data. 

This CVE is especially for Quarkus as Quarkus extensively uses the Vert.x duplicated context to implement context propagation. With the new semantic data from one transaction can leak to the data from another transaction. From a Vert.x point of view, this new semantic clarifies the behavior. 

A significant amount of data is stored in the duplicated context, including request scope, security details, and metadata. Duplicating a duplicated context is rather rare and is only done in a few places:

- Quarkus REST Client when using OTel (but it's the same transaction, so no leak)
- Quarkus Messaging connectors
- Quarkus SmallRye Health (same transaction, so no leak)



### Patches

After discussion with the Vert.x team, the change will be rolled back in Vert.x 4.x. A new API will be added to Vert.x 5 do distinguish the 2 cases.

### Workarounds

When duplicating a duplicated context, the following code can be done to avoid the potential leak:

```java
((ContextInternal) VertxContext.getRootContext(ctx)).duplicate()
```

This workaround would not be required once the Vert.x version containing the fix will be included. Note that the workaround would still work. 


### References

This issue have been reported in https://github.com/quarkusio/quarkus/issues/48227.

## References
- https://github.com/quarkusio/quarkus/security/advisories/GHSA-9623-mj7j-p9v4
- https://nvd.nist.gov/vuln/detail/CVE-2025-49574
- https://github.com/quarkusio/quarkus/issues/48227
- https://github.com/quarkusio/quarkus/pull/48486
- https://github.com/quarkusio/quarkus/commit/2b58f59f4bf0bae7d35b1abb585b65f2a66787d1
- https://github.com/quarkusio/quarkus/commit/31e8a3bfcf4e223788615d5ce25eb929ca251275
- https://github.com/quarkusio/quarkus/commit/d1ee57e7b826872b6355cfec0ae13465840e232c
- https://github.com/quarkusio/quarkus
- https://github.com/quarkusio/quarkus/releases/tag/3.24.1
