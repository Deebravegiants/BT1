# [M] Kargo has Missing Authorization Vulnerabilities in Approval & Promotion REST API Endpoints

## Summary
Severity: Medium
Advisory: GHSA-5vvm-67pj-72g4
CVE: CVE-2026-27111
CWE: CWE-862
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:N/SI:L/SA:N (CVSS_V4)
Published: 2026-02-19
Source: https://github.com/advisories/GHSA-5vvm-67pj-72g4
Type: github-advisory

## Affected
- Go: `github.com/akuity/kargo` — affected >=1.9.0 <1.9.3

## Details
## Summary

Kargo's authorization model includes a `promote` verb -- a non-standard Kubernetes ["dolphin verb"](https://www.aquasec.com/blog/kubernetes-verbs/) -- that gates the ability to advance `Freight` through a promotion pipeline. This verb exists to separate the ability to _manage_ promotion-related resources from the ability to _trigger_ promotions, enabling fine-grained access control over what is often a sensitive operation.

The `promote` verb is correctly enforced in Kargo's legacy gRPC API. However, three endpoints in the newer REST API omit this check, relying only on standard Kubernetes RBAC for the underlying resource operations (`patch` on `freights/status` or `create` on `promotions`). This permits users who hold those standard permissions -- but who were deliberately _not_ granted `promote` -- to bypass the intended authorization boundary.

The affected endpoints are:

1. `POST /v1beta1/projects/{project}/freight/{freight}/approve`

    Approves `Freight` for promotion to a specific `Stage`.

    The endpoint is intended to require both `patch` permission on `Freight` status and `promote` permission on the target `Stage`, but asserts only the former.

2. `POST /v1beta1/projects/{project}/stages/{stage}/promotions`

    Promotes `Freight` to a specific `Stage`.

    The endpoint is intended to require both `create` permission on `Promotion` resources and `promote` permission on the target `Stage`, but asserts only the former.

3. `POST /v1beta1/projects/{project}/stages/{stage}/promotions/downstream`

    Promotes `Freight` to all `Stage`s immediately downstream of a given `Stage`.

    The endpoint is intended to require both `create` permission on `Promotion` resources and `promote` permission on each downstream `Stage`, but asserts only the former.

## Base Metrics

The following sections provide the rationale for the values selected for each of CVSS v4's base metrics.

### Attack Vector (AV): Network

The affected endpoints are part of Kargo's newer REST API, which is served over HTTP/HTTPS. (The analogous endpoints of the legacy gRPC API correctly check `promote` permission and are not affected.) No local or physical access is required.

### Attack Complexity (AC): Low

The attack requires only well-formed API requests to the affected endpoints.

### Attack Requirements (AT): None

No specific environmental conditions are required beyond those that are typical for any Kargo instance.

### Privileges Required (PR): Low

The attacker must hold permissions to patch `Freight` status and/or create `Promotion` resources. These are standard operational permissions commonly granted to some Kargo users and do not represent what CVSS formally considers administrative or elevated access.

### User Interaction (UI): None

The attack is fully automated via API calls. No other user needs to take any action.

### Confidentiality Impact to Vulnerable System (VC): None

The vulnerability does not expose any data from the Kargo control plane.

### Integrity Impact to Vulnerable System (VI): Low

The attacker can coerce a `Stage` into a state it might not otherwise transition to. This constitutes bounded state corruption within a single Project. Kargo itself continues to function correctly.

### Availability Impact to Vulnerable System (VA): None

`Promotion` resources created by exploitation of this vulnerability consume the same controller resources as a legitimate `Promotion` would. A user with proper `promote` permissions could generate identical load. The vulnerability does not introduce any new avenue for resource exhaustion.

### Confidentiality Impact to Subsequent Systems (SC): None

The vulnerability does not provide any mechanism for the attacker to read data from downstream systems.

### Integrity Impact to Subsequent Systems (SI): Low

Critically, the attacker does not control the _content_ of `Freight` resources without artifact repositories also having been compromised. In isolation, which is how vulnerabilities are scored, the worst consequence of a successful attack is downstream systems (e.g. Argo CD) deploying incorrect revisions of artifacts, which in some cases should have been rejected by bypassed segments of the promotion pipeline. Though the operational consequences land on subsequent systems, they are bounded by the attacker's inability to inject arbitrary content.

### Availability Impact to Subsequent Systems (SA): None

The attack does not provide any mechanism to degrade the availability of downstream systems beyond what could be achieved with legitimately promoted `Freight`.

## Mitigating Factors

- Only the REST API endpoints introduced in v1.9.0 are affected. The legacy gRPC API and the Kargo UI (which uses the gRPC API) correctly enforce the `promote` permission check and are not vulnerable.

- The window of affected versions is narrow: v1.9.0 through v1.9.2.

- Exploitation requires authentication to the Kargo API server and specific operational permissions (`patch` on `freights/status` or `create` on `promotions`). Anonymous or minimally privileged users cannot exploit this vulnerability.

- Impact is bounded to a single Project. The `promote` bypass does not enable cross-Project access or escalation beyond the namespace in which the attacker already holds the prerequisite permissions.

- There is no evidence of exploitation in the wild.

## References
- https://github.com/akuity/kargo/security/advisories/GHSA-5vvm-67pj-72g4
- https://nvd.nist.gov/vuln/detail/CVE-2026-27111
- https://github.com/akuity/kargo/commit/833314cad5513d48d89431493325ae44c1324a49
- https://github.com/akuity/kargo
