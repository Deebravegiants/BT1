# [C] Kargo has an Authorization Bypass Vulnerability in Batch Resource Creation API Endpoints

## Summary
Severity: Critical
Advisory: GHSA-7g9x-cp9g-92mr
CVE: CVE-2026-27112
CWE: CWE-863
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-7g9x-cp9g-92mr
Type: github-advisory

## Affected
- Go: `github.com/akuity/kargo` — affected >=1.9.0-rc.1 <1.9.3
- Go: `github.com/akuity/kargo` — affected >=1.8.0-rc.1 <1.8.11
- Go: `github.com/akuity/kargo` — affected >=1.7.0 <1.7.8

## Details
## Summary

The batch resource creation endpoints of both Kargo's legacy gRPC API and newer REST API accept multi-document YAML payloads. When either endpoint creates a `Project` resource, creation of subsequent resources from that same payload belonging in that Project's underlying Kubernetes namespace, by design, proceeds using the API server's own permissions. The creator of a new Project automatically becomes its administrator, but those permissions are granted asynchronously by the management controller. The design choice to create the affected resources using the API server's own permissions averts a race and is contextually appropriate.

Specially crafted payloads can manifest a bug present in the logic of both endpoints to inject arbitrary resources (of specific types only) into the underlying namespace of an _existing_ Project using the API server's own permissions when that behavior was _not_ intended. Critically, an attacker may exploit this as a vector for elevating their own permissions, which can then be leveraged to achieve remote code execution or secret exfiltration. Exfiltrated artifact repository credentials can be leveraged, in turn, to execute further attacks.

In some configurations of the Kargo control plane's underlying Kubernetes cluster, elevated permissions may additionally be leveraged to achieve remote code execution or secret exfiltration using `kubectl`. This can reduce the complexity of the attack, however, worst case scenarios remain entirely achievable even without this.

## Base Metrics

The following sections provide the rationale for the values selected for each of CVSS v4's base metrics.

### Attack Vector (AV): Network

The affected endpoints are served by the Kargo API server over HTTP/HTTPS. No local or physical access is required.

### Attack Complexity (AC): Low

Exploitation requires only a specially crafted YAML payload sent to an affected API endpoint.

### Attack Requirements (AT): None

No specific environmental conditions are required beyond those that are typical for any Kargo instance.

### Privileges Required (PR): Low

The attack relies only on the ability to authenticate to the Kargo API server along with basic permissions that are typically granted to all Kargo users.

### User Interaction (UI): None

The attack is fully automated via API calls. No other user needs to take any action.

### Confidentiality Impact to Vulnerable System (VC): High

Elevated permissions enable secret exfiltration from any Kargo Project.

### Integrity Impact to Vulnerable System (VI): High

Elevated permissions enable tampering, up to and including remote code execution, as well as secret exfiltration from any Kargo Project. Project secrets often include credentials having write permissions to GitOps repositories. Such secrets may enable pushing configurations that impact the integrity of the vulnerable system, including Kargo Projects, Kargo control plane components, and the Kargo control plane's underlying Kubernetes cluster.

Note: Because it is an integral component of Kargo's control plane, the underlying Kubernetes cluster has been counted as a component of the vulnerable system instead of a subsequent system.

### Availability Impact to Vulnerable System (VA): High

Elevated permissions enable tampering, up to and including remote code execution, as well as secret exfiltration from any Kargo Project. Project secrets often include credentials having write permissions to GitOps repositories. Such secrets may enable pushing configurations that impact the availability of the vulnerable system, including Kargo control plane components and the Kargo control plane's underlying Kubernetes cluster.

### Confidentiality Impact to Subsequent Systems (SC): High

Secrets exfiltrated from Project namespaces typically contain credentials for external systems. These may enable exfiltration of further confidential information from those systems.

### Integrity Impact to Subsequent Systems (SI): High

Elevated permissions enable tampering, up to and including remote code execution, as well as secret exfiltration from any Kargo Project. Project secrets often include credentials having write permissions to GitOps repositories. Such secrets may enable pushing configurations that impact the integrity of subsequent systems.

### Availability Impact to Subsequent Systems (SA): High

Elevated permissions enable tampering, up to and including remote code execution, as well as secret exfiltration from any Kargo Project. Project secrets often include credentials having write permissions to GitOps repositories. Such secrets may enable pushing configurations that impact the availability of subsequent systems.

## Mitigating Factors

- Exploitation requires authentication to the Kargo API server. Anonymous access is not sufficient.

- The most severe consequences of this vulnerability depend on a privilege escalation path (via `RoleBinding` injection) that was not identified by the original reporter, suggesting it is not immediately obvious from the bug alone.

- There is no evidence of exploitation in the wild.

## References
- https://github.com/akuity/kargo/security/advisories/GHSA-7g9x-cp9g-92mr
- https://nvd.nist.gov/vuln/detail/CVE-2026-27112
- https://github.com/akuity/kargo/commit/155c6852ffbffa2902f18e6c7add91a846e8d344
- https://github.com/akuity/kargo
