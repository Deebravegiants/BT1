# [M] epa4all-client: Unauthenticated REST API for Patient Record Writes

## Summary
Severity: Medium
Advisory: GHSA-c82x-f4xr-qv33
CVE: CVE-2026-47672
CWE: CWE-306
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-c82x-f4xr-qv33
Type: github-advisory

## Affected
- Maven: `com.oviva.telematik:epa4all-rest-service` — affected >=0

## Details
### Impact
Any network-reachable caller can write arbitrary documents to any patient's electronic
health record accessible by the institution's SMC-B card. In a misconfigured deployment
(e.g., following the production Docker example in the README), this is exploitable from
the local network without credentials.

### Patches
- [#43](https://github.com/oviva-ag/epa4all-client/pull/43)

### Workarounds
Use network policies or proxies to enforce service-to-service authentication via e.g. mTLS.
- run the service in an isolated network namespace e.g. as Kubernetes sidecar
- service-mesh with corresponding policies

### References
- MS-OVIVA-EPA4ALL-8b2af7


### Credits
[Machine Spirits](https://machinespirits.com/) ([contact@machinespirits.de](mailto:contact@machinespirits.de))

- Dr. rer. nat. Simon Weber
- Dipl.-Inf. Volker Schönefeld
- Chiara Fliegner

## References
- https://github.com/oviva-ag/epa4all-client/security/advisories/GHSA-c82x-f4xr-qv33
- https://nvd.nist.gov/vuln/detail/CVE-2026-47672
- https://github.com/oviva-ag/epa4all-client/pull/43
- https://github.com/oviva-ag/epa4all-client
