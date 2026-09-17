# [M] CVE-2020-24613

## Summary
Severity: Medium
Advisory: CVE-2020-24613
CVSS: 6.8 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-08-24
Source: https://osv.dev/vulnerability/CVE-2020-24613
Type: osv

## Details
wolfSSL before 4.5.0 mishandles TLS 1.3 server data in the WAIT_CERT_CR state, within SanityCheckTls13MsgReceived() in tls13.c. This is an incorrect implementation of the TLS 1.3 client state machine. This allows attackers in a privileged network position to completely impersonate any TLS 1.3 servers, and read or modify potentially sensitive information between clients using the wolfSSL library and these TLS servers.

## References
- https://research.nccgroup.com/2020/08/24/technical-advisory-wolfssl-tls-1-3-client-man-in-the-middle-attack/
