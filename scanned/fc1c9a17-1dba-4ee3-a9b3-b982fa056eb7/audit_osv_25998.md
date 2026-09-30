# [M] Wazuh vulnerable to  NULL Pointer Dereference in wazuh-analysisd

## Summary
Severity: Medium
Advisory: CVE-2023-49275
Aliases: GHSA-4mq7-w9r6-9975
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-04-19
Source: https://osv.dev/vulnerability/CVE-2023-49275
Type: osv

## Details
Wazuh is a free and open source platform used for threat prevention, detection, and response. A NULL pointer dereference was detected during fuzzing of the analysis engine, allowing malicious clients to DoS the analysis engine. The bug occurs when `analysisd` receives a syscollector message with the `hotfix` `msg_type` but lacking a `timestamp`. It uses `cJSON_GetObjectItem()` to get the `timestamp` object item and dereferences it without checking for a `NULL` value. A malicious client can DoS the analysis engine. This vulnerability is fixed in 4.7.1.

## References
- https://github.com/wazuh/wazuh/blob/e1d5231b31b68a75f3b8b33f833155b362411078/src/analysisd/decoders/syscollector.c#L1573
- https://github.com/wazuh/wazuh/blob/e1d5231b31b68a75f3b8b33f833155b362411078/src/analysisd/decoders/syscollector.c#L1578
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/49xxx/CVE-2023-49275.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-4mq7-w9r6-9975
- https://nvd.nist.gov/vuln/detail/CVE-2023-49275
