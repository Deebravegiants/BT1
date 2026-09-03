# [C] Potential remote code exploit in log4j dependency

## Summary
Severity: Critical
Chain: Ethereum
Component: Consensys/teku
CVE: CVE-2021-44228
Published: 2021-12-10
Source: https://github.com/Consensys/teku/security/advisories/GHSA-mwfw-vm54-g3p7
Type: github-advisory

## Details
### Impact
A zero-day vulnerability has been published in log4j, a very popular logging library that is used by Teku.

While Teku does include a version of log4j that is affected, at this stage we don't believe Teku is itself vulnerable because of the way we use the logging library. However out of an abundance of caution we have released an emergency patch ([21.12.1](https://github.com/ConsenSys/teku/releases/tag/21.12.1)) to guarantee it is not possible to exploit.

The log4j exploit would allow remote code execution, potentially allowing an attacker to access validator signing keys.

### Patches
Teku 21.12.1 includes an updated version of log4j and configuration to guarantee this vulnerability is not exploitable.

For binary downloads of Teku 21.12.1 see: https://github.com/ConsenSys/teku/releases/tag/21.12.1

### Workarounds
Users can apply this mitigation now with any version of Teku by setting the Java option `-Dlog4j2.formatMsgNoLookups=true`. The easiest way to do this is by setting the `JAVA_OPTS` environment variable or the `TEKU_OPTS` environment variable. You may have already used this to set a `-Xmx` value.

Command line example:
JAVA_OPTS="-Dlog4j2.formatMsgNoLookups=true" teku --network mainnet

Or with an -Xmx value:
JAVA_OPTS="-Dlog4j2.formatMsgNoLookups=true -Xmx4g" teku

Systemd config example:
Environment='JAVA_OPTS="-Dlog4j2.formatMsgNoLookups=true"'

Or with an -Xmx value:
Environment='JAVA_OPTS="-Dlog4j2.formatMsgNoLookups=true" "-Xmx4g'

### References
https://nvd.nist.gov/vuln/detail/CVE-2021-44228
https://www.lunasec.io/docs/blog/log4j-zero-day/

### For more information
If you have any questions or comments about this advisory:
* Contact us in the #teku channel on [Discord](https://discord.gg/7hPv2T6)
