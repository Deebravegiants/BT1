# [H] Graylog concurrent PDF report rendering can leak other users' reports

## Summary
Severity: High
Advisory: GHSA-vggm-3478-vm5m
CVE: CVE-2024-52506
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-11-18
Source: https://github.com/advisories/GHSA-vggm-3478-vm5m
Type: github-advisory

## Affected
- Maven: `org.graylog:graylog-parent` — affected >=6.1.0 <6.1.2

## Details
### Impact

The reporting functionality in Graylog allows the creation and scheduling of reports which contain dashboard widgets displaying individual log messages or metrics aggregated from fields of multiple log messages. This functionality, as included in Graylog 6.1.0 & 6.1.1, is vulnerable to information leakage triggered by multiple concurrent report rendering requests from authorized users.

When multiple report renderings are requested at the same start time, the headless browser instance used to render the PDF will be reused. Depending on the timing, either a check for the browser instance "freshness" hits, resulting in an error instead of the report being returned, or one of the concurrent report rendering requests "wins" and this report is returned for all report rendering requests that do not return an error. This might lead to one user getting the report of a different user, potentially leaking indexed log messages or aggregated data that this user normally has no access to.

### Patches
This problem is fixed in Graylog 6.1.2.

### Workarounds
There is no known workaround besides disabling the reporting functionality.

### References

## References
- https://github.com/Graylog2/graylog2-server/security/advisories/GHSA-vggm-3478-vm5m
- https://nvd.nist.gov/vuln/detail/CVE-2024-52506
- https://github.com/Graylog2/graylog2-server
- https://www.vicarius.io/vsociety/posts/cve-2024-52506-detect-graylog-vulnerability
- https://www.vicarius.io/vsociety/posts/cve-2024-52506-mitigate-graylog-vulnerability
