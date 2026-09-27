# [H] dmlc/dgl Vulnerable to Remote Code Execution by Pickle Deserialization via rpc.recv_request()

## Summary
Severity: High
Advisory: GHSA-3x5x-fw77-g54c
CWE: CWE-502
Ecosystem: PyPI
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-03-05
Source: https://github.com/advisories/GHSA-3x5x-fw77-g54c
Type: github-advisory

## Affected
- PyPI: `dgl` — affected >=0

## Details
### Impact
Dgl implements rpc server (start_server() in rpc_server.py) for supporting the RPC communications among different remote users over networks. It relies on pickle serialize and deserialize to pack and unpack network messages. The is a known risk in pickle deserialization functionality that can be used for remote code execution.

### Patches
TBD.

### Workarounds
When running DGL distributed training and inference (DistDGL) make sure you do not assign public IPs to any instance in the cluster.

### References
Issue #7874

### Reported by
Pinji Chen ([cpj24@mails.tsinghua.edu.cn](mailto:cpj24@mails.tsinghua.edu.cn)) from NISL lab (https://netsec.ccert.edu.cn/about) at Tsinghua University

## References
- https://github.com/dmlc/dgl/security/advisories/GHSA-3x5x-fw77-g54c
- https://github.com/dmlc/dgl/issues/7874
- https://github.com/dmlc/dgl
