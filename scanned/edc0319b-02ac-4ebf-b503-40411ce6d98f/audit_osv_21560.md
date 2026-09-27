# [M] CVE-2021-43979

## Summary
Severity: Medium
Advisory: CVE-2021-43979
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2021-11-17
Source: https://osv.dev/vulnerability/CVE-2021-43979
Type: osv

## Details
Styra Open Policy Agent (OPA) Gatekeeper through 3.7.0 mishandles concurrency, sometimes resulting in incorrect access control. The data replication mechanism allows policies to access the Kubernetes cluster state. During data replication, OPA/Gatekeeper does not wait for the replication to finish before processing a request, which might cause inconsistencies between the replicated resources in OPA/Gatekeeper and the resources actually present in the cluster. Inconsistency can later be reflected in a policy bypass. NOTE: the vendor disagrees that this is a vulnerability, because Kubernetes states are only eventually consistent

## References
- https://github.com/hkerma/opa-gatekeeper-concurrency-issue
- https://github.com/open-policy-agent/gatekeeper/releases
