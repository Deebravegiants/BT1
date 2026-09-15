# [C] laf logs leak

## Summary
Severity: Critical
Advisory: CVE-2023-50253
Aliases: GHSA-g9c8-wh35-g75f
CVSS: 9.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:H/I:H/A:H)
Published: 2024-01-03
Source: https://osv.dev/vulnerability/CVE-2023-50253
Type: osv

## Details
Laf is a cloud development platform. In the Laf version design, the log uses communication with k8s to quickly retrieve logs from the container without the need for additional storage. However, in version 1.0.0-beta.13 and prior, this interface does not verify the permissions of the pod, which allows authenticated users to obtain any pod logs under the same namespace through this method, thereby obtaining sensitive information printed in the logs. As of time of publication, no known patched versions exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/50xxx/CVE-2023-50253.json
- https://github.com/labring/laf/security/advisories/GHSA-g9c8-wh35-g75f
- https://nvd.nist.gov/vuln/detail/CVE-2023-50253
- https://github.com/labring/laf/pull/1468
