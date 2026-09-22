# [C] 5.1.1 Open ports to the internet

## Summary
Severity: Critical
Source: https://github.com/tintinweb/smart-contract-vulndb
Type: audit-issue

## Details
**Severity:** Critical Risk
**Context:** linux-ec2-cdk/lib/linux-ec2-cdk-stack.ts#L49-L
**Description:** The following ports will be open from the internet (0.0.0.0/0) and would allow anyone to access
any service running under them.

- 443 tcp - https
- 9100-9104 tcp - beacon Node metrics port
- 9091 tcp - prometheus
- 3100 tcp - grafana
- 8545 tcp - execution layer rpc
- 9001 tcp - prometheus
- 5052 - beacon API
**Recommendation:** Remove the ports from the security group and keep public facing ports to the minimum (the
API ports currently exposed can be easily used to DDoS the node and should definitely not be exposed). In this
case, the P2P ports 9001(tcp/udp) and 30303(tcp/udp). Port forwarding via SSH can be used to access these
ports in a secure way.
**Redacted:** Fixed in PR 56.
**Spearbit:** The recommendation was followed and a fix was applied in PR 56 at commit 6b5f37a6. Only the P2P
ports are now directly exposed directly to the Internet.
