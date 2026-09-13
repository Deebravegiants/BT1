# [M] Wazuh agent enrollment NULL pointer dereference via malformed manager response

## Summary
Severity: Medium
Advisory: CVE-2026-54084
Aliases: GHSA-ppc7-hj9v-vx39
CVSS: 5.3 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2026-08-27
Source: https://osv.dev/vulnerability/CVE-2026-54084
Type: osv

## Details
Wazuh is an open-source security platform providing unified XDR and SIEM protection for endpoints and cloud workloads. In versions 4.0.0 through 4.14.6, a malicious or man-in-the-middle enrollment manager can crash a Wazuh agent during enrollment by returning a malformed key response with fewer than four fields, causing a NULL pointer dereference. The  w_enrollment_process_agent_key()  routine splits the manager-provided key into four space-separated fields but does not verify that all fields are present before passing them to validators. Because OS_StrBreak() leaves missing trailing entries as NULL and OS_IsValidName() calls strlen() on its argument without a NULL check, a response such as  OSSEC K:'1'  reaches OS_IsValidName(NULL) and terminates the agent process. Since Wazuh permits enrollment against an unverified manager when no CA certificate is configured, an attacker operating a rogue manager or intercepting the enrollment flow can deterministically crash agents, resulting in denial of service. This issue is fixed in version 4.14.7.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/54xxx/CVE-2026-54084.json
- https://github.com/wazuh/wazuh/security/advisories/GHSA-ppc7-hj9v-vx39
- https://nvd.nist.gov/vuln/detail/CVE-2026-54084
- https://github.com/wazuh/wazuh/commit/7dfbb4a292bc6ae8e3bb4c1982f687f35216a748
