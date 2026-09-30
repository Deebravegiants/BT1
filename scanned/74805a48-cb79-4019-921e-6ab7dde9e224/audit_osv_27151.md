# [M] Denial of Service through Data corruption in gRPC-C++

## Summary
Severity: Medium
Advisory: CVE-2024-11407
CVSS: 6.0 (CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H/S:N/AU:N/R:A/RE:L/U:Green)
Published: 2024-11-26
Source: https://osv.dev/vulnerability/CVE-2024-11407
Type: osv

## Details
There exists a denial of service through Data corruption in gRPC-C++ - gRPC-C++ servers with transmit zero copy enabled through the channel arg GRPC_ARG_TCP_TX_ZEROCOPY_ENABLED can experience data corruption issues. The data sent by the application may be corrupted before transmission over the network thus leading the receiver to receive an incorrect set of bytes causing RPC requests to fail. We recommend upgrading past commit e9046b2bbebc0cb7f5dc42008f807f6c7e98e791

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/11xxx/CVE-2024-11407.json
- https://nvd.nist.gov/vuln/detail/CVE-2024-11407
- https://github.com/grpc/grpc/commit/e9046b2bbebc0cb7f5dc42008f807f6c7e98e791
- https://github.com/grpc/grpc
