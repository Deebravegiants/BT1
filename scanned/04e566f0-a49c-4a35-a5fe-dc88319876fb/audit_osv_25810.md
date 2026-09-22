# [C] Remote code execution in XXL-RPC

## Summary
Severity: Critical
Advisory: CVE-2023-45146
Aliases: GHSA-f984-3wx8-grp9
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2023-10-18
Source: https://osv.dev/vulnerability/CVE-2023-45146
Type: osv

## Details
XXL-RPC is a high performance, distributed RPC framework. With it, a TCP server can be set up using the Netty framework and the Hessian serialization mechanism. When such a configuration is used, attackers may be able to connect to the server and provide malicious serialized objects that, once deserialized, force it to execute arbitrary code. This can be abused to take control of the machine the server is running by way of remote code execution. This issue has not been fixed.

## References
- https://www.vicarius.io/vsociety/posts/xxl-rpc-rce-cve-2023-45146
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/45xxx/CVE-2023-45146.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-45146
- https://securitylab.github.com/advisories/GHSL-2023-052_XXL-RPC/
