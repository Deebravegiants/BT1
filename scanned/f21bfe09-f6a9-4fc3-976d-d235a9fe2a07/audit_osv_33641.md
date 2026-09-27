# [C] Apache NuttX RTOS: examples/xmlrpc: Fix calls buffers size.

## Summary
Severity: Critical
Advisory: CVE-2025-47869
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2025-06-16
Source: https://osv.dev/vulnerability/CVE-2025-47869
Type: osv

## Details
Improper Restriction of Operations within the Bounds of a Memory Buffer vulnerability was discovered in Apache NuttX RTOS apps/exapmles/xmlrpc application. In this example application device stats structure that stored remotely provided parameters had hardcoded buffer size which could lead to buffer overflow. Structure members buffers were updated to valid size of CONFIG_XMLRPC_STRINGSIZE+1.

This issue affects Apache NuttX RTOS users that may have used or base their code on example application as presented in releases from 6.22 before 12.9.0.

Users of XMLRPC in Apache NuttX RTOS are advised to review their code 
for this pattern and update buffer sizes as presented in the version of 
the example in release 12.9.0.

## References
- http://www.openwall.com/lists/oss-security/2025/06/14/2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/47xxx/CVE-2025-47869.json
- https://lists.apache.org/thread/306qcqyc3bpb2ozh015yxjo9kqs4jbvj
- https://nvd.nist.gov/vuln/detail/CVE-2025-47869
- https://github.com/apache/nuttx-apps/pull/3027
