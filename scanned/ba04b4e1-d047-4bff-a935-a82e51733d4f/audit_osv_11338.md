# [H] CVE-2017-7458

## Summary
Severity: High
Advisory: CVE-2017-7458
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-06-26
Source: https://osv.dev/vulnerability/CVE-2017-7458
Type: osv

## Details
The NetworkInterface::getHost function in NetworkInterface.cpp in ntopng before 3.0 allows remote attackers to cause a denial of service (NULL pointer dereference and application crash) via an empty field that should have contained a hostname or IP address.

## References
- https://github.com/ntop/ntopng/blob/3.0/CHANGELOG.md
- https://github.com/ntop/ntopng/commit/01f47e04fd7c8d54399c9e465f823f0017069f8f
