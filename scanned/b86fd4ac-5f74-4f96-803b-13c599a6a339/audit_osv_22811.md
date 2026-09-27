# [H] Buffer Overflow in `ProcessRadioRxDone` in LoRaMac-node

## Summary
Severity: High
Advisory: CVE-2022-39274
Aliases: GHSA-7vv8-73pc-63c2
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-10-06
Source: https://osv.dev/vulnerability/CVE-2022-39274
Type: osv

## Details
LoRaMac-node is a reference implementation and documentation of a LoRa network node. Versions of LoRaMac-node prior to 4.7.0 are vulnerable to a buffer overflow. Improper size validation of the incoming radio frames can lead to an 65280-byte out-of-bounds write. The function `ProcessRadioRxDone` implicitly expects incoming radio frames to have at least a payload of one byte or more. An empty payload leads to a 1-byte out-of-bounds read of user controlled content when the payload buffer is reused. This allows an attacker to craft a FRAME_TYPE_PROPRIETARY frame with size -1 which results in an 65280-byte out-of-bounds memcopy likely with partially controlled attacker data. Corrupting a large part if the data section is likely to cause a DoS. If the large out-of-bounds write does not immediately crash the attacker may gain control over the execution due to now controlling large parts of the data section. Users are advised to upgrade either by updating their package or by manually applying the patch commit `e851b079`.

## References
- https://github.com/Lora-net/LoRaMac-node/releases/tag/v4.7.0
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/39xxx/CVE-2022-39274.json
- https://github.com/Lora-net/LoRaMac-node/security/advisories/GHSA-7vv8-73pc-63c2
- https://nvd.nist.gov/vuln/detail/CVE-2022-39274
- https://github.com/Lora-net/LoRaMac-node/commit/e851b079c82ba1bcf3f4d291ab69a571b0bf458a
