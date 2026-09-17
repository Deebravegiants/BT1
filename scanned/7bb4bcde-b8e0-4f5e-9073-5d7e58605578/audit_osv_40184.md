# [M] ptp: Potential Denial of Service via PTP Interval Shift

## Summary
Severity: Medium
Advisory: CVE-2026-5072
Aliases: GHSA-3v98-458v-388r
CVSS: 6.5 (CVSS:3.1/AV:A/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-05-22
Source: https://osv.dev/vulnerability/CVE-2026-5072
Type: osv

## Details
A bitwise shift vulnerability in Zephyr's PTP subsystem allows a remote attacker to cause undefined behavior and potential system crashes. An attacker sends a crafted PTP_MSG_MANAGEMENT message to set an unvalidated negative log_announce_interval value in the port's data set. When a subsequent PTP_MSG_ANNOUNCE message is processed, port_timer_set_timeout_random computes a timeout as NSEC_PER_SEC >> -log_seconds; if the attacker-supplied value is sufficiently negative (e.g., -127), the shift amount exceeds the 64-bit integer width, triggering undefined behavior in C. This can cause a system crash via a compiler-generated illegal instruction trap on some architectures, or produce an erroneous zero timeout leading to resource starvation loops or other logical errors.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/5xxx/CVE-2026-5072.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-3v98-458v-388r
- https://nvd.nist.gov/vuln/detail/CVE-2026-5072
- https://github.com/zephyrproject-rtos/zephyr
