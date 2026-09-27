# [C] CVE-2021-29462

## Summary
Severity: Critical
Advisory: CVE-2021-29462
Aliases: GHSA-6hqq-w3jq-9fhg
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-04-20
Source: https://osv.dev/vulnerability/CVE-2021-29462
Type: osv

## Details
The Portable SDK for UPnP Devices is an SDK for development of UPnP device and control point applications. The server part of pupnp (libupnp) appears to be vulnerable to DNS rebinding attacks because it does not check the value of the `Host` header. This can be mitigated by using DNS revolvers which block DNS-rebinding attacks. The vulnerability is fixed in version 1.14.6 and later.

## References
- http://www.openwall.com/lists/oss-security/2021/04/20/4
- https://github.com/pupnp/pupnp/security/advisories/GHSA-6hqq-w3jq-9fhg
