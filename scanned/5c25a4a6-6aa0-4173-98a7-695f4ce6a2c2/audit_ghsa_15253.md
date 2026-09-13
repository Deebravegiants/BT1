# [M] Hwameistor Potential Permission Leakage of Cluster Level 

## Summary
Severity: Medium
Advisory: GHSA-mgwr-h7mv-fh29
CVE: CVE-2024-45054
CWE: CWE-200, CWE-266
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-08-29
Source: https://github.com/advisories/GHSA-mgwr-h7mv-fh29
Type: github-advisory

## Affected
- Go: `github.com/hwameistor/hwameistor` — affected >=0 <0.14.6

## Details
### Impact
_What kind of vulnerability is it? Who is impacted?_
This ClusterRole has * verbs of * resources. If a malicious user can access the worker node which has hwameistor's deployment, he/she can abuse these excessive permissions to do whatever he/she likes to the whole cluster, resulting in a cluster-level privilege escalation.

### Patches
_Has the problem been patched? What versions should users upgrade to?_
>= v0.14.6

### Workarounds
_Is there a way for users to fix or remediate the vulnerability without upgrading?_
Update and Limit the ClusterRole using [security-role](https://github.com/hwameistor/hwameistor/blob/main/helm/hwameistor/templates/clusterrole.yaml).

### References
_Are there any links users can visit to find out more?_
issues:
https://github.com/hwameistor/hwameistor/issues/1457
https://github.com/hwameistor/hwameistor/issues/1460

also reported by users via mails: 
[sparkEchooo](https://github.com/sparkEchooo), [younaman](https://github.com/younaman)

## References
- https://github.com/hwameistor/hwameistor/security/advisories/GHSA-mgwr-h7mv-fh29
- https://nvd.nist.gov/vuln/detail/CVE-2024-45054
- https://github.com/hwameistor/hwameistor/issues/1457
- https://github.com/hwameistor/hwameistor/issues/1460
- https://github.com/hwameistor/hwameistor/commit/edf4cebed73cadd230bf97eab65c5311f2858450
- https://github.com/hwameistor/hwameistor
- https://github.com/hwameistor/hwameistor/blob/main/helm/hwameistor/templates/clusterrole.yaml
