# [C] Apache bRPC: ServerOptions.pid_file may cause arbitrary code execution

## Summary
Severity: Critical
Advisory: CVE-2023-31039
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-05-08
Source: https://osv.dev/vulnerability/CVE-2023-31039
Type: osv

## Details
Security vulnerability in Apache bRPC <1.5.0 on all platforms allows attackers to execute arbitrary code via ServerOptions::pid_file.
An attacker that can influence the ServerOptions pid_file parameter with which the bRPC server is started can execute arbitrary code with the permissions of the bRPC process.

Solution:
1. upgrade to bRPC >= 1.5.0, download link:  https://dist.apache.org/repos/dist/release/brpc/1.5.0/ https://dist.apache.org/repos/dist/release/brpc/1.5.0/ 
2. If you are using an old version of bRPC and hard to upgrade, you can apply this patch:  https://github.com/apache/brpc/pull/2218 https://github.com/apache/brpc/pull/2218

## References
- http://www.openwall.com/lists/oss-security/2023/05/08/1
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/31xxx/CVE-2023-31039.json
- https://lists.apache.org/thread/jqpttrqbc38yhckgp67xk399hqxnz7jn
- https://nvd.nist.gov/vuln/detail/CVE-2023-31039
