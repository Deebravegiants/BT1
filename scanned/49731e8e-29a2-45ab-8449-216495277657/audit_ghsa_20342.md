# [M] Weak private key generation in SSH.NET

## Summary
Severity: Medium
Advisory: GHSA-72p8-v4hg-v45p
CVE: CVE-2022-29245
CWE: CWE-330, CWE-338
Ecosystem: NuGet
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-06-01
Source: https://github.com/advisories/GHSA-72p8-v4hg-v45p
Type: github-advisory

## Affected
- NuGet: `SSH.NET` — affected >=0 <2020.0.2

## Details
During an **X25519** key exchange, the client’s private is generated with [**System.Random**](https://docs.microsoft.com/en-us/dotnet/api/system.random):

```cs
var rnd = new Random();
_privateKey = new byte[MontgomeryCurve25519.PrivateKeySizeInBytes];
rnd.NextBytes(_privateKey);
```

Source: [KeyExchangeECCurve25519.cs](https://github.com/sshnet/SSH.NET/blob/bc99ada7da3f05f50d9379f2644941d91d5bf05a/src/Renci.SshNet/Security/KeyExchangeECCurve25519.cs#L51)  
Source commit: https://github.com/sshnet/SSH.NET/commit/b58a11c0da55da1f5bad46faad2e9b71b7cb35b3

[**System.Random**](https://docs.microsoft.com/en-us/dotnet/api/system.random) is not a cryptographically secure random number generator, it must therefore not be used for cryptographic purposes.

### Impact
When establishing an SSH connection to a remote host, during the X25519 key exchange, the private key is generated with
a weak random number generator whose seed can be bruteforced. This allows an attacker able to eavesdrop the
communications to decrypt them.

### Workarounds
To ensure you're not affected by this vulnerability, you can disable support for `curve25519-sha256` and `curve25519-sha256@libssh.org` key exchange algorithms by invoking the following method before a connection is established:
```cs
private static void RemoveUnsecureKEX(BaseClient client)
{
    client.ConnectionInfo.KeyExchangeAlgorithms.Remove("curve25519-sha256");
    client.ConnectionInfo.KeyExchangeAlgorithms.Remove("curve25519-sha256@libssh.org");
}
```

### Thanks

This issue was initially reported by **Siemens AG, Digital Industries**, shortly followed by @yaumn-synacktiv.

## References
- https://github.com/sshnet/SSH.NET/security/advisories/GHSA-72p8-v4hg-v45p
- https://nvd.nist.gov/vuln/detail/CVE-2022-29245
- https://github.com/sshnet/SSH.NET/commit/03c6d60736b8f7b42e44d6989a53f9b644a091fb
- https://github.com/sshnet/SSH.NET/commit/f1f273cf349532b9d41c1de51d3b83a9accedc88
- https://github.com/sshnet/SSH.NET
- https://github.com/sshnet/SSH.NET/blob/bc99ada7da3f05f50d9379f2644941d91d5bf05a/src/Renci.SshNet/Security/KeyExchangeECCurve25519.cs#L51
- https://github.com/sshnet/SSH.NET/releases/tag/2020.0.2
