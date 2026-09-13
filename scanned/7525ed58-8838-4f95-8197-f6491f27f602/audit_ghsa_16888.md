# [M] Temporal Server Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-wmxc-v39r-p9wf
CVE: CVE-2024-2689
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-04-04
Source: https://github.com/advisories/GHSA-wmxc-v39r-p9wf
Type: github-advisory

## Affected
- Go: `github.com/temporalio/temporal` — affected >=1.22.0-rc1 <1.22.7
- Go: `github.com/temporalio/temporal` — affected >=1.21.0 <1.21.6
- Go: `github.com/temporalio/temporal` — affected >=0 <1.20.5

## Details
Denial of Service in Temporal Server prior to version 1.20.5, 1.21.6, and 1.22.7 allows an authenticated user who has permissions to interact with workflows and has crafted an invalid UTF-8 string for submission to potentially cause a crashloop. If left unchecked, the task containing the invalid UTF-8 will become stuck in the queue, causing an increase in queue lag. Eventually, all processes handling these queues will become stuck and the system will run out of resources. The workflow ID of the failing task will be visible in the logs, and can be used to remove that workflow as a mitigation. Version 1.23 is not impacted. In this context, a user is an operator of Temporal Server.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-2689
- https://github.com/temporalio/temporal/commit/2099dfd945accbf794404c3b8d990d109de19f06
- https://github.com/temporalio/temporal/commit/679e3dc2ca8bd39e02c760f686cc8807f817bbfd
- https://github.com/temporalio/temporal/commit/f1fab97129f964dcca17d1f7c344f38666d1ee5f
- https://github.com/temporalio/temporal
- https://github.com/temporalio/temporal/releases
