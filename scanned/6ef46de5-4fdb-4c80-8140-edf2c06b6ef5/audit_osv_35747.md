# [M] Databroker 0.6.1 PublishValue missing data_point panic

## Summary
Severity: Medium
Advisory: CVE-2026-13699
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-14
Source: https://osv.dev/vulnerability/CVE-2026-13699
Type: osv

## Details
In Eclipse KUKSA Databroker version 0.6.1, the kuksa.val.v2.VAL/PublishValue gRPC handler fails to validate the existence of the optional data_point field in PublishValueRequest. When a request contains a valid signal_id but omits data_point, the server directly calls unwrap() on request.data_point, triggering a panic in the Tokio worker thread. This issue can be triggered by any client holding a valid JWT token. Unauthenticated or invalid-token requests are rejected and do not reach the vulnerable path. The panic causes the individual gRPC call to be cancelled but does not terminate the Databroker process, which remains available for subsequent requests.

## References
- https://gitlab.eclipse.org/security/cve-assignment/-/work_items/148
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/13xxx/CVE-2026-13699.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-13699
