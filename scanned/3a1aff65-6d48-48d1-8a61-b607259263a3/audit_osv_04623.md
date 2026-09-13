# [H] BIT-dotnet-2026-25667

## Summary
Severity: High
Advisory: BIT-dotnet-2026-25667
Aliases: BIT-dotnet-sdk-2026-25667, CVE-2026-25667
Ecosystem: Bitnami
Published: 2026-04-16
Source: https://osv.dev/vulnerability/BIT-dotnet-2026-25667
Type: osv

## Affected
- Bitnami: `dotnet` — affected >=9.0.0 <9.0.11

## Details
ASP.NET Core Kestrel in Microsoft .NET 8.0 before 8.0.22 and .NET 9.0 before 9.0.11 allows a remote attacker to cause excessive CPU consumption by sending a crafted QUIC packet, because of an incorrect exit condition for HTTP/3 Encoder/Decoder stream processing.

## References
- https://github.com/IsaJafarov/Kestrel-DoS
- https://github.com/dotnet/aspnetcore/commit/96ccc40a0e095424b19506e8268b9b1a3e23d6a7#diff-667d5b3693f93a0f706ab211428998b210862f9b885d917104d2013118312626
- https://nvd.nist.gov/vuln/detail/CVE-2026-25667
- https://github.com/IsaJafarov/Q3Fuzz
