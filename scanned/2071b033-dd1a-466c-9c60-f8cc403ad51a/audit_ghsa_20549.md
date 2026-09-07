# [M] Impersonation of other users (passing XBOX Live authentication) by theft of logins in PocketMine-MP

## Summary
Severity: Medium
Advisory: GHSA-h79x-98r2-g6qc
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-01-21
Source: https://github.com/advisories/GHSA-h79x-98r2-g6qc
Type: github-advisory

## Affected
- Packagist: `pocketmine/pocketmine-mp` — affected >=3.0.0 <4.0.0

## Details
# Impact
Minecraft Bedrock authentication and its protocol encryption are inseparably linked. One is not complete without the other.

This vulnerability affects servers which are able to be directly connected to via the internet (i.e. not behind a proxy).

If you are using a proxy, please check that it supports protocol encryption and that it is enabled.

# Technical details
<details>
<summary>click to expand</summary>

## Basics

1. The client generates a private ECC key `clientPriv` which it uses to complete ECDH for encryption.
2. A JWT containing the public key `clientPub` corresponding to this key is signed by Microsoft servers with the [Mojang root public key](https://github.com/pmmp/PocketMine-MP/blob/stable/src/network/mcpe/auth/ProcessLoginTask.php#L42) `mojangPub`.
3. The server verifies that the token was issued by Microsoft servers by verifying the JWT signature with `mojangPub`.

## Why this is a problem
However, this only ensures that the token was issued by Microsoft. It does _not_ ensure that the client actually possesses the private key corresponding to the public key in the token.
In a login replay attack, the attacker sends a login captured from another session. This login is valid because it is verifiable by `mojangPub`; however, without encryption, the server doesn't know that the client actually possesses `clientPriv`, and the authenticity of the client cannot be verified.

## How encryption prevents the attack

1. The server calculates a shared secret for encryption using ECDH of `serverPriv` and `clientPub`.
2. It then signs a return token using `serverPriv` and sends this to the client, along with `serverPub`.
3. The client then verifies the JWT using `serverPub`, and calculates the same shared secret as the server using `clientPriv` and `serverPub`.

If the client does not possess `clientPriv` (i.e. because it replayed a stolen login), then the session cannot proceed once encryption is enabled, since the client cannot calculate the shared secret needed to decrypt the server packets and encrypt its own packets.

**Since PM3 does not implement protocol encryption, this means that ALL versions of PM3 are affected by this login stealing attack.**

## How does the attacker capture a login in the first place?
The typical way to do this would be to trick a player into joining a server controlled by the attacker. This would allow the attacker to grab the login from the connection and store it for future use.

## Are the logins valid forever?
No. All the JWTs have expiry dates after which they cannot be used. These expiry dates are typically 2-3 days after the token was issued by XBOX servers. PocketMine-MP 3.x does verify these expiry dates, so the use-by dates of these attacks are limited.

</details>

# Patches
This problem has been fixed in all 4.x versions by implementing Minecraft protocol encryption.

~This has not yet been addressed on 3.x, but since this vulnerability is already public knowledge, the advisory has been released early to make sure people are aware of it and the mitigation steps they can take.~

Update 2022-01-22: This has been fixed on 3.x by d28be4eaf24a890f7ef110a51181a3d806a6acca.

# Workarounds
- Use a proxy that supports encryption such as [gophertunnel](https://github.com/Sandertv/gophertunnel) between your server and players. Make sure that the server only accepts connections from the proxy. If the proxy is on the same machine as the server, you can use `server-ip=127.0.0.1` to ensure that only the proxy can create connections for you.

The following things may help mitigate the problem:
- Verify that the `LoginPacket` `serverAddress` field is the same as the server's exposed domain name. For example: https://github.com/JustTalDevelops/AntiLoginForger
**WARNING: THIS DOES NOT SOLVE THE ROOT ISSUE. YOU WILL REMAIN VULNERABLE UNLESS YOU UPGRADE.**

# For more information
If you have any questions or comments about this advisory:
* Email us at [team@pmmp.io](mailto:team@pmmp.io)

## References
- https://github.com/pmmp/PocketMine-MP/security/advisories/GHSA-h79x-98r2-g6qc
- https://github.com/pmmp/PocketMine-MP/issues/4580
- https://github.com/pmmp/PocketMine-MP
