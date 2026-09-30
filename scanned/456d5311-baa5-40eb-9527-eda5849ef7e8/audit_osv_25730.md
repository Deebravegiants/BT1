# [M] Snapshot signature not including HeadID will allow replay attacks

## Summary
Severity: Medium
Advisory: CVE-2023-42806
Aliases: GHSA-gr36-mc6v-72qq
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-09-21
Source: https://osv.dev/vulnerability/CVE-2023-42806
Type: osv

## Details
Hydra is the layer-two scalability solution for Cardano. Prior to version 0.13.0, not signing and verifying `$\mathsf{cid}$` allows an attacker (which must be a participant of this head) to use a snapshot from an old head instance with the same participants to close the head or contest the state with it. This can lead to an incorrect distribution of value (= value extraction attack; hard, but possible) or prevent the head to finalize because the value available is not consistent with the closed utxo state (= denial of service; easy). A patch is planned for version 0.13.0. As a workaround, rotate keys between heads so not to re-use keys and not result in the same multi-signature participants.

## References
- https://github.com/input-output-hk/hydra/blob/ec6c7a2ab651462228475d0b34264e9a182c22bb/hydra-node/src/Hydra/HeadLogic.hs#L357
- https://github.com/input-output-hk/hydra/blob/ec6c7a2ab651462228475d0b34264e9a182c22bb/hydra-node/src/Hydra/Snapshot.hs#L50-L54
- https://github.com/input-output-hk/hydra/blob/ec6c7a2ab651462228475d0b34264e9a182c22bb/hydra-plutus/src/Hydra/Contract/Head.hs#L583-L599
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42806.json
- https://github.com/input-output-hk/hydra/security/advisories/GHSA-gr36-mc6v-72qq
- https://nvd.nist.gov/vuln/detail/CVE-2023-42806
