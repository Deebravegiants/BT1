# [M] ConnectBot SSH Client Library: Unbounded SSH field lengths can cause excessive memory allocation

## Summary
Severity: Medium
Advisory: GHSA-ch3q-cw5r-f4hg
CVE: CVE-2026-54700
CWE: CWE-20, CWE-789
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-ch3q-cw5r-f4hg
Type: github-advisory

## Affected
- Maven: `org.connectbot.sshlib:sshlib` — affected >=0

## Details
## Summary

The SSH protocol parser trusted attacker-controlled length and count fields without first checking that the declared values fit within the containing packet.

When a client connects to a malicious or compromised SSH server, the server can send a small, malformed packet containing an inner field whose declared length is much larger than the packet itself. The Kaitai Struct Java runtime attempts to allocate a byte array using the declared length before it discovers that the input is truncated. A sufficiently large value can therefore cause excessive memory allocation or an uncaught `OutOfMemoryError`, potentially terminating the application process that uses the library.

Applications that enable SSH agent forwarding have an additional attack path: the connected server can send malformed agent protocol messages containing the same class of oversized inner length.

## Details

SSH uses unsigned 32-bit length prefixes for strings and other protocol structures. Before the fix, several Kaitai Struct definitions passed these lengths directly to generated parsing code. For example, the byte-string definition read a `uint32` followed by an array of that size without validating the size against the bytes remaining in the current stream.

The SSH transport limits the size of an outer packet, but an inner field in that packet could still declare a length approaching the Java array size limit. The Kaitai runtime allocates the destination array before reading from the bounded input stream. Consequently, an attacker does not need to transmit an equally large packet to trigger the allocation attempt.

Malformed count fields could also cause parsers to attempt an unreasonable number of repeated elements. The fix validates both byte lengths and element counts against the size of their containing stream.

Parsing failures previously surfaced inconsistently as unchecked runtime exceptions. The fixed version converts malformed SSH packets to a transport protocol error and returns an SSH agent failure response for malformed agent requests.

## Attack Requirements

For the general SSH packet path:

- A user or application must initiate a connection to an attacker-controlled or compromised SSH server.
- Authentication is not required.
- No optional library feature is required.
- The server only needs to return a malformed SSH packet containing an oversized inner length or count.

For the agent protocol path, SSH agent forwarding must additionally be enabled.

## Impact

Successful exploitation can cause excessive heap allocation and loss of availability of the application process. In constrained environments, a single small malicious packet can cause an `OutOfMemoryError`.

No confidentiality or integrity impact has been demonstrated.

## Remediation

Upgrade to version `0.3.1` or later.

The fix:

- Validates length-prefixed fields against the remaining bytes in their containing Kaitai stream.
- Validates repeated-element counts against the minimum encoded size of each element.
- Validates SSH transport and agent frame lengths and padding constraints.
- Converts malformed SSH packet parsing failures into `TransportException`.
- Returns `SSH_AGENT_FAILURE` for malformed forwarded-agent requests instead of allowing parser exceptions to escape.

## References
- https://github.com/connectbot/cbssh/security/advisories/GHSA-ch3q-cw5r-f4hg
- https://github.com/connectbot/cbssh
- https://github.com/connectbot/cbssh/releases/tag/v0.3.1
