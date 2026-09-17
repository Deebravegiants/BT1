# [M] xblock-lti-consumer contain Missing Authorization in Grade Pass Back Implementation

## Summary
Severity: Medium
Advisory: CVE-2023-23611
Aliases: GHSA-7j9p-67mm-5g87, PYSEC-2023-21
CVSS: 5.4 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N)
Published: 2023-01-25
Source: https://osv.dev/vulnerability/CVE-2023-23611
Type: osv

## Details
LTI Consumer XBlock implements the consumer side of the LTI specification enabling integration of third-party LTI provider tools. Versions 7.0.0 and above, prior to 7.2.2, are vulnerable to Missing Authorization.  Any LTI tool that is integrated with on the Open edX platform can post a grade back for any LTI XBlock so long as it knows or can guess the block location for that XBlock. An LTI tool submits scores to the edX platform for line items. The code that uploads that score to the LMS grade tables determines which XBlock to upload the grades for by reading the resource_link_id field of the associated line item. The LTI tool may submit any value for the resource_link_id field, allowing a malicious LTI tool to submit scores for any LTI XBlock on the platform. The impact is a loss of integrity for LTI XBlock grades. This issue is patched in 7.2.2. No workarounds exist.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/23xxx/CVE-2023-23611.json
- https://github.com/openedx/xblock-lti-consumer/security/advisories/GHSA-7j9p-67mm-5g87
- https://nvd.nist.gov/vuln/detail/CVE-2023-23611
