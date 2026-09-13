# [H] CVE-2023-0957

## Summary
Severity: High
Advisory: CVE-2023-0957
CVSS: 8.2 (CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:H/I:H/A:L)
Published: 2023-03-03
Source: https://osv.dev/vulnerability/CVE-2023-0957
Type: osv

## Details
An issue was discovered in Gitpod versions prior to release-2022.11.2.16. There is a Cross-Site WebSocket Hijacking (CSWSH) vulnerability that allows attackers to make WebSocket connections to the Gitpod JSONRPC server using a victim’s credentials, because the Origin header is not restricted. This can lead to the extraction of data from workspaces, to a full takeover of the workspace.

## References
- https://app.safebase.io/portal/71ccd717-aa2d-4a1e-942e-c768d37e9e0c/preview?product=default&orgId=71ccd717-aa2d-4a1e-942e-c768d37e9e0c&tcuUid=1d505bda-9a38-4ca5-8724-052e6337f34d
- https://github.com/gitpod-io/gitpod/releases/tag/release-2022.11.2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/0xxx/CVE-2023-0957.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-0957
- https://github.com/gitpod-io/gitpod/commit/12956988eec0031f42ffdfa3bdc3359f65628f9f
- https://github.com/gitpod-io/gitpod/commit/673ab6856fa04c13b7b1f2a968e4d090f1d94e4f
- https://github.com/gitpod-io/gitpod/pull/16378
- https://github.com/gitpod-io/gitpod/pull/16405
- https://snyk.io/blog/gitpod-remote-code-execution-vulnerability-websockets/
