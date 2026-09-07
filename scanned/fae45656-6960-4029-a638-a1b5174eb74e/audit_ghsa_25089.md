# [H] Code Injection in Masuit.Tools.Core

## Summary
Severity: High
Advisory: GHSA-vh38-ghx6-vmvg
CVE: CVE-2022-21167
CWE: CWE-94
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-03
Source: https://github.com/advisories/GHSA-vh38-ghx6-vmvg
Type: github-advisory

## Affected
- NuGet: `Masuit.Tools.Core` — affected >=0

## Details
All versions of package Masuit.Tools.Core are vulnerable to Arbitrary Code Execution via the ReceiveVarData<T> function in the SocketClient.cs component. The socket client in the package can pass in the payload via the user-controllable input after it has been established, because this socket client transmission does not have the appropriate restrictions or type bindings for the BinaryFormatter.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-21167
- https://github.com/ldqk/Masuit.Tools
- https://github.com/ldqk/Masuit.Tools/blob/327f42b9f20f25bb66188672199c8265fc968d91/Masuit.Tools.Abstractions/Net/SocketClient.cs%23L197
- https://snyk.io/vuln/SNYK-DOTNET-MASUITTOOLSCORE-2316875
