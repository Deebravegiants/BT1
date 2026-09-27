# [C] Access Control Bypass in Onedev

## Summary
Severity: Critical
Advisory: CVE-2022-39205
Aliases: GHSA-4f9h-h82c-4xm2
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2022-09-13
Source: https://osv.dev/vulnerability/CVE-2022-39205
Type: osv

## Details
Onedev is an open source, self-hosted Git Server with CI/CD and Kanban. In versions of Onedev prior to 7.3.0 unauthenticated users can take over a OneDev instance if there is no properly configured reverse proxy. The /git-prereceive-callback endpoint is used by the pre-receive git hook on the server to check for branch protections during a push event. It is only intended to be accessed from localhost, but the check relies on the X-Forwarded-For header. Invoking this endpoint leads to the execution of one of various git commands. The environment variables of this command execution can be controlled via query parameters. This allows attackers to write to arbitrary files, which can in turn lead to the execution of arbitrary code. Such an attack would be very hard to detect, which increases the potential impact even more. Users are advised to upgrade. There are no known workarounds for this issue.

## References
- https://github.com/theonedev/onedev/releases/tag/v7.3.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39205.json
- https://github.com/theonedev/onedev/security/advisories/GHSA-4f9h-h82c-4xm2
- https://nvd.nist.gov/vuln/detail/CVE-2022-39205
- https://github.com/theonedev/onedev/commit/f1e97688e4e19d6de1dfa1d00e04655209d39f8e
- https://blog.sonarsource.com/onedev-remote-code-execution/
