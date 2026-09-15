# [M] Knative Serving vulnerable to attacker-controlled pod causing denial of service of autoscaler

## Summary
Severity: Medium
Advisory: GHSA-qmvj-4qr9-v547
CVE: CVE-2023-48713
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-27
Source: https://github.com/advisories/GHSA-qmvj-4qr9-v547
Type: github-advisory

## Affected
- Go: `knative.dev/serving` — affected >=0 <0.39.0

## Details
### Summary
A vulnerability was fond in Knative Serving that could allow an attacker to crash the Knative Serving autoscaler resulting in a denial of service. The attacker would need to have compromised one pod in the Knative Serving deployment, and with that position they could launch the attack against the autoscaler. 
When the autoscaler scrapes the metrics of pods, it sends a request to the `/metrics` endpoint of each pod and reads the response. The attacker would need to detect the request from the autoscaler to the `/metrics` endpoint of the pod they had compromised and send a malicious response back to the autoscaler. At this point, the autoscaler would crash. The root cause of the vulnerability was a memory exhaustion issue in the autoscaler that the attacker could trigger with the malicious reponse.

The vulnerability would allow a privilege escalation by the attacker from controlling one point to having negative impact on the entire Knative Serving deployment.

### Impact
All users are vulnerable to this; Users that have not had any of their pods compromised are not at risk of this vulnerability.  

### Mitigation
The vulnerability has been patched in v1.10.5, v1.11.3 and v1.12.0

### Credits
The vulnerability was reported by Ada Logics during an ongoing security audit of Knative involving Ada Logics, the Knative maintainers, OSTIF and CNCF.

## References
- https://github.com/knative/serving/security/advisories/GHSA-qmvj-4qr9-v547
- https://nvd.nist.gov/vuln/detail/CVE-2023-48713
- https://github.com/knative/serving/commit/012ee2509231b80b7842139bfabc30516d3026ca
- https://github.com/knative/serving/commit/101f814112b9ca0767f457e7e616b46205551cf1
- https://github.com/knative/serving/commit/fff40ef7bac9be8380ec3d1c70fc15b57093382a
- https://github.com/knative/serving
