# [M] CVE-2025-25774

## Summary
Severity: Medium
Advisory: CVE-2025-25774
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2025-03-12
Source: https://osv.dev/vulnerability/CVE-2025-25774
Type: osv

## Details
An issue was discovered in Open5GS v2.7.2. When a UE switches between two gNBs and sends a handover request at a specific time, it may cause an exception in the AMF's internal state machine, leading to an AMF crash and resulting in a Denial of Service (DoS).

## References
- https://github.com/guoweifk/BugReport/blob/main/Open5GS%20AMF%20Denial%20of%20Service%20via%20GMM%20State%20Handling%20in%20Handover
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/25xxx/CVE-2025-25774.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-25774
- https://github.com/open5gs/open5gs/issues/3671
- https://github.com/open5gs/open5gs/commit/2e68706f1eea029d5172ccad946e78b352c031d0
