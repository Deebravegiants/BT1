# [M] Bluetooth Mesh PB-ADV: invalidated provisioning link kept alive indefinitely, blocking (re)provisioning (DoS)

## Summary
Severity: Medium
Advisory: CVE-2026-10675
Aliases: GHSA-4rwg-6mr4-55hc
CVSS: 4.3 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2026-07-21
Source: https://osv.dev/vulnerability/CVE-2026-10675
Type: osv

## Details
In Zephyr's Bluetooth Mesh PB-ADV provisioning bearer (subsys/bluetooth/mesh/pb_adv.c), prov_msg_recv() rescheduled the provisioning protocol watchdog timer unconditionally at the top of the function, before the FCS check and before the ADV_LINK_INVALID check. Once a provisioning attempt fails, prov_failed() sets ADV_LINK_INVALID and the only recovery path is the protocol timer firing (protocol_timeout -> prov_link_close -> close_link -> reset_adv_link and re-enabling of scanning and the unprovisioned device beacon).

A remote, unauthenticated attacker on the BLE advertising channel can first induce a provisioning failure (e.g. with a malformed generic-provisioning PDU) and then transmit any FCS-valid PB-ADV transaction PDU on the same link ID more often than once per protocol timeout (60 s, or 120 s for OOB input/output). Because each such packet reset the timer even on an invalidated link, protocol_timeout never fired, the dead link was never torn down, and the device remained pinned in an un-provisionable state with its unprovisioned beacon disabled and new Link Open requests rejected.

PB-ADV PDUs are processed without authentication and the FCS is a keyless CRC, so no pairing or prior trust is required and the attacker chooses the link ID itself. The impact is a persistent denial of provisioning/re-provisioning service; there is no memory-safety, confidentiality, or integrity impact.

The vulnerable code shipped in releases through v4.4.1. The fix moves the timer reschedule to after the ADV_LINK_INVALID check (and the FCS check before the reset) so an invalidated link can no longer be kept alive by incoming packets.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/10xxx/CVE-2026-10675.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-4rwg-6mr4-55hc
- https://nvd.nist.gov/vuln/detail/CVE-2026-10675
- https://github.com/zephyrproject-rtos/zephyr/commit/3f3c37edf80262b838ef5402fec9880c07892e4e
- https://github.com/zephyrproject-rtos/zephyr
