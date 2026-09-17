# [H] rPGP Potential Resource Exhaustion when handling Untrusted Messages

## Summary
Severity: High
Advisory: GHSA-4grw-m28r-q285
CVE: CVE-2024-53857
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-12-05
Source: https://github.com/advisories/GHSA-4grw-m28r-q285
Type: github-advisory

## Affected
- crates.io: `pgp` — affected >=0 <0.14.2

## Details
During a security audit, [Radically Open Security](https://www.radicallyopensecurity.com/) discovered two vulnerabilities which allow attackers to trigger resource exhaustion vulnerabilities in `rpgp` by providing crafted messages. This affects general message parsing and decryption with symmetric keys.

### Impact
Affected `rpgp` versions do not correctly set upper limits on the total reserved amount of memory when parsing long sequences of partial OpenPGP packets, which can grow to to several GiB in size. Additionally, up to 4GiB of memory is reserved for OpenPGP packets of fixed size with large length fields, even if less data is received. 
Depending on existing message size restrictions and available system resources, this can cause out-of-memory conditions and crash the `rpgp` process or cause other system instability through memory resource exhaustion when parsing crafted messages.

Affected `rpgp` versions are susceptible to excessive memory allocation with values of up to 2TiB or long processing times for some decryption operations which involve the [Argon2 function](https://datatracker.ietf.org/doc/html/rfc9580.html#name-argon2). An attacker can provide a valid `Symmetric Key Encrypted Session Key` packet (SKESK) which uses `Argon2` for String-to-Key hashing with parameters that are excessive, but within specification limits of the RFC9580 OpenPGP standard. Since `rpgp` did not further restrict the Argon2 parameters, this can cause out-of-memory conditions and crash the `rpgp` process. Under some conditions,   the memory resource exhaustion may trigger other system instability. Alternatively, this can make the program unresponsive via long computations. The attacker needs to trick a victim into attempting decryption, but does not require knowledge of the symmetric secret used by the victim.

There is no impact to confidentiality or integrity security properties.

### Versions and Patches

The impact details on the message parsing component varies with different versions. We've confirmed some of the problematic behavior on older versions such as `v0.10.0` and see all recent versions as affected in some form.  

The affected `Argon2` functionality was introduced with `v0.12.0-alpha.1`, earlier versions are not vulnerable.

The vulnerabilities have been fixed with version `0.14.2`. We recommend all users to upgrade to this version.

### References


The security audit was made possible by the [NLnet Foundation NGI Zero Core](https://nlnet.nl/core/) grant program [for rpgp](https://nlnet.nl/project/rPGP-cryptorefresh/).

## References
- https://github.com/rpgp/rpgp/security/advisories/GHSA-4grw-m28r-q285
- https://nvd.nist.gov/vuln/detail/CVE-2024-53857
- https://github.com/rpgp/rpgp
