# [C] Open ports to the internet

## Summary
Severity: Critical
Contest weight: 0.1220
Dataset id: 13933
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
The following ports will be open from the internet (0.0.0.0/0) and would allow anyone to access any service running under them.
• 443 tcp - https
• 9100-9104 tcp - beacon Node metrics port
• 9091 tcp - prometheus
• 3100 tcp - grafana
• 8545 tcp - execution layer rpc
• 9001 tcp - prometheus
• 5052 - beacon API

## Recommendation
Remove the ports from the security group and keep public facing ports to the minimum (the API ports currently exposed can be easily used to DDoS the node and should definitely not be exposed). In this case, the P2P ports 9001(tcp/udp) and 30303(tcp/udp). Port forwarding via SSH can be used to access these ports in a secure way.
