# [H] Hydra's contestation period in head datum can be modified during Close transaction, allowing malicious participant to freely modify the contestation deadline

## Summary
Severity: High
Advisory: CVE-2023-42448
Aliases: GHSA-mgcx-6p7h-5996
CVSS: 8.1 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:H/A:H)
Published: 2023-10-04
Source: https://osv.dev/vulnerability/CVE-2023-42448
Type: osv

## Details
Hydra is the layer-two scalability solution for Cardano. Prior to version 0.13.0, the specification states that the contestation period in the datum of the UTxO at the head validator must stay unchanged as the state progresses from Open to Closed (Close transaction), but no such check appears to be performed in the `checkClose` function of the head validator. This would allow a malicious participant to modify the contestation deadline of the head to either allow them to fanout the head without giving another participant the chance to contest, or prevent any participant from ever redistributing the funds locked in the head via a fan-out. Version 0.13.0 contains a patch for this issue.

## References
- https://github.com/input-output-hk/hydra/blob/master/CHANGELOG.md#0130---2023-10-03
- https://github.com/input-output-hk/hydra/blob/master/hydra-plutus/src/Hydra/Contract/Head.hs#L284-L296
- https://github.com/input-output-hk/hydra/blob/master/hydra-plutus/src/Hydra/Contract/Head.hs#L320-L323
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/42xxx/CVE-2023-42448.json
- https://github.com/input-output-hk/hydra/security/advisories/GHSA-mgcx-6p7h-5996
- https://nvd.nist.gov/vuln/detail/CVE-2023-42448
- https://github.com/input-output-hk/hydra/commit/2f45529729e28254a62f7a7c8d6649066923ed1f
