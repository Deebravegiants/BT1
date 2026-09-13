# [M] fabric8 kubernetes-client vulnerable 

## Summary
Severity: Medium
Advisory: GHSA-98g7-rxmf-rrxm
CVE: CVE-2021-4178
CWE: CWE-502, CWE-94
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-07-15
Source: https://github.com/advisories/GHSA-98g7-rxmf-rrxm
Type: github-advisory

## Affected
- Maven: `io.fabric8:kubernetes-client` — affected >=5.0.0-beta-1 <5.0.3
- Maven: `io.fabric8:kubernetes-client` — affected >=5.1.0 <5.1.2
- Maven: `io.fabric8:kubernetes-client` — affected >=5.2.0 <5.3.2
- Maven: `io.fabric8:kubernetes-client` — affected >=5.5.0 <5.7.4
- Maven: `io.fabric8:kubernetes-client` — affected >=5.8.0 <5.8.1
- Maven: `io.fabric8:kubernetes-client` — affected >=5.9.0 <5.10.2
- Maven: `io.fabric8:kubernetes-client` — affected >=5.11.0 <5.11.2

## Details
fabric8 Kubernetes client had an arbitrary code execution flaw in versions 5.0.0-beta-1 and higher. Attackers could potentially insert malicious YAMLs due to misconfigured YAML parsing.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-4178
- https://github.com/fabric8io/kubernetes-client/issues/3653
- https://github.com/fabric8io/kubernetes-client/commit/445103004d1ed3153d5abb272473451d05891e39
- https://access.redhat.com/security/cve/cve-2021-4178
- https://bugzilla.redhat.com/show_bug.cgi?id=2034388
- https://github.com/fabric8io/kubernetes-client
- https://www.mend.io/vulnerability-database/CVE-2021-4178
