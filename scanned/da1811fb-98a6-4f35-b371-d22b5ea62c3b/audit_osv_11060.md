# [H] CVE-2017-5887

## Summary
Severity: High
Advisory: CVE-2017-5887
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-04-06
Source: https://osv.dev/vulnerability/CVE-2017-5887
Type: osv

## Details
WebSocket.swift in Starscream before 2.0.4 allows an SSL Pinning bypass because pinning occurs in the stream function (this is too late; pinning should occur in the initStreamsWithData function).

## References
- http://seclists.org/bugtraq/2017/Apr/67
- https://github.com/daltoniam/Starscream/releases/tag/2.0.4
- https://github.com/daltoniam/Starscream/commit/dbeb1190b8dcbff4f0b797f9e9d9b9b864d1f0d6
