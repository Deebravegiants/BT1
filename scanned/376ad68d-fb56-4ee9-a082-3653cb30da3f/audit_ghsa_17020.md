# [H] CoreWCF NetFraming based services can leave connections open when they should be closed

## Summary
Severity: High
Advisory: GHSA-32jq-mv89-5rx7
CVE: CVE-2024-28252
CWE: CWE-404
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-15
Source: https://github.com/advisories/GHSA-32jq-mv89-5rx7
Type: github-advisory

## Affected
- NuGet: `CoreWCF.NetFramingBase` — affected >=1.4.0 <1.4.2
- NuGet: `CoreWCF.NetFramingBase` — affected >=1.5.0 <1.5.2

## Details
### Impact
If you have a NetFraming based CoreWCF service, extra system resources could be consumed by connections being left established instead of closing or aborting them. There are two scenarios when this can happen. When a client established a connection to the service and sends no data, the service will wait indefinitely for the client to initiate the NetFraming session handshake. Additionally, once a client has established a session, if the client doesn't send any requests for the period of time configured in the binding ReceiveTimeout, the connection is not properly closed as part of the session being aborted.  
The bindings affected by this behavior are NetTcpBinding, NetNamedPipeBinding, and UnixDomainSocketBinding. Only NetTcpBinding has the ability to accept non local connections.

### Patches
The currently supported versions of CoreWCF are v1.4.x and v1.5.x. The fix can be found in v1.4.2 and v1.5.2 of the CoreWCF packages.

### Workarounds
There are no workarounds.

### References
https://github.com/CoreWCF/CoreWCF/issues/1345

## References
- https://github.com/CoreWCF/CoreWCF/security/advisories/GHSA-32jq-mv89-5rx7
- https://nvd.nist.gov/vuln/detail/CVE-2024-28252
- https://github.com/CoreWCF/CoreWCF/issues/1345
- https://github.com/CoreWCF/CoreWCF
