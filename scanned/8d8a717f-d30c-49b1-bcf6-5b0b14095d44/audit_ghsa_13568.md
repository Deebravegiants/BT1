# [H] Apollo Router vulnerable to Improper Check or Handling of Exceptional Conditions

## Summary
Severity: High
Advisory: GHSA-r344-xw3p-2frj
CVE: CVE-2023-45812
CWE: CWE-703, CWE-754
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-19
Source: https://github.com/advisories/GHSA-r344-xw3p-2frj
Type: github-advisory

## Affected
- crates.io: `apollo-router` — affected >=1.31.0 <1.33.0

## Details
### Impact
The Apollo Router is a configurable, high-performance graph router written in Rust to run a federated supergraph that uses Apollo Federation. Affected versions are subject to a Denial-of-Service (DoS) type vulnerability which causes the Router to panic and terminate when a multi-part response is sent. When users send queries to the router that uses the `@defer` or Subscriptions, the Router will panic.
 
To be vulnerable, users of Router must have a coprocessor with `coprocessor.supergraph.response` configured in their `router.yaml` and also to support either `@defer` or Subscriptions.  

### Patches
Router version 1.33.0 has a fix for this vulnerability. https://github.com/apollographql/router/pull/4014 fixes the issue.  

### Workarounds
For affected versions, avoid using the coprocessor supergraph response:
```yml
# do not use this stage in your coprocessor configuration
coprocessor:
  supergraph:
    response:
``` 

Or you can disable defer and subscriptions support:
```yml
# disable defer and subscriptions:
supergraph:
  defer_support: false # enabled by default
subscription:
  enabled: false # disabled by default
```
and continue to use the coprocessor supergraph response.
### References
https://github.com/apollographql/router/issues/4013

## References
- https://github.com/apollographql/router/security/advisories/GHSA-r344-xw3p-2frj
- https://nvd.nist.gov/vuln/detail/CVE-2023-45812
- https://github.com/apollographql/router/issues/4013
- https://github.com/apollographql/router/pull/4014
- https://github.com/apollographql/router/commit/b917b8c117b46a2d508428c0856f4927dfcfc341
- https://github.com/apollographql/router
