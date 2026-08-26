# [M] SEC-50 RLPx AES CTR keystream reusage #1315. (Case for private network)

## Summary
Severity: Medium
Chain: Ethereum
Component: hyperledger/besu
Published: 2026-08-10
Source: https://github.com/besu-eth/besu/security/advisories/GHSA-v5gq-r843-8f73
Type: github-advisory

## Details
Hyperledger Besu's RLPx frame encryption initialises the AES-CTR encryptor and decryptor with the same key (aes-secret) and the same all-zeros IV. Because AES-CTR produces a deterministic keystream from key + IV + counter, both the egress (outgoing) and ingress (incoming) streams generate identical keystreams. An attacker who can observe both sides of a connection and knows any plaintext in one direction
  can recover plaintext in the other direction by XORing the two ciphertexts against the known plaintext.

  This is a known limitation of the current RLPx specification, acknowledged explicitly in the devp2p RLPx spec: "The frame encryption/MAC scheme is considered 'broken' because aes-secret and mac-secret are reused for both reading and writing." No Ethereum client has shipped a fix to date, as doing so would require a coordinated cross-client protocol change.

  CVE: CVE-2015-20112

  Attack preconditions

  The attacker must be a passive eavesdropper with visibility into both sides of the TCP connection — for example, a compromised network device, a malicious insider with traffic mirroring access, or an operator of a node on the same layer-2 segment. Active man-in-the-middle is not required.

  Additionally, the attacker must know some plaintext at a given byte offset in one direction. RLPx Hello messages have predictable structure and length, making this feasible in practice.

  Scope

  - Confidentiality: affected — frame payloads can be decrypted under the above conditions.
  - Integrity: not affected — egress and ingress MACs are derived separately and seeded from distinct handshake material; a passive attacker cannot forge frames.
  - Authentication: not affected — the ECIES handshake uses proper asymmetric encryption and is unaffected by this issue.

  Impact

  On public networks, most RLPx traffic (blocks, transactions, receipts) is public data, so decryption provides little meaningful advantage to an attacker.

  On private networks carrying confidential data (e.g., private transactions, sensitive state), the impact is higher. An attacker with network-level access to a private deployment could recover transaction content or other sensitive payload data.

  Mitigation (current)

  Private network operators should enforce strict network-level access controls to ensure that no untrusted party can observe both sides of a peer connection. TLS-terminated VPN tunnels or IP allowlisting at the network perimeter reduce the eavesdropping risk.

Related geth issue - https://github.com/ethereum/go-ethereum/issues/1315

from https://github.com/ethereum/devp2p/issues/32 :
"The two sides of a RLPx connection generate two CTR streams from the same key, nonce and IV.
If an attacker knows one plaintext, he can decrypt unknown plaintexts of the reused keystream.
Separate keys needs to be used for each stream. See for example the TLS 1.2 RFC 5246 section 6.3."

  References


_Trimmed to 38 lines — full report: https://github.com/besu-eth/besu/security/advisories/GHSA-v5gq-r843-8f73_
