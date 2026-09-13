# [M] Out-of-bounds stack read and write in Zephyr WNC-M14A2A modem socket-notify parsing

## Summary
Severity: Medium
Advisory: CVE-2026-12519
Aliases: GHSA-8hrc-q8cp-6xhf
CVSS: 5.0 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-12519
Type: osv

## Details
The WNC-M14A2A LTE-M modem driver mishandles unsolicited %NOTIFYEV: events in on_cmd_socknotifyev() (drivers/modem/vendor_standalone/wncm14a2a.c). The response line is linearized into a fixed 40-byte stack buffer via net_buf_linearize(), which caps the copy at 39 bytes and returns out_len <= 39. The two quote-delimiter scanning loops, however, were bounded by len — the full CR/LF-delimited frame length returned by net_buf_findcrlf() — rather than by out_len.

When a %NOTIFYEV: line longer than 39 bytes contains no " within the linearized region, the loop indices p1/p2 walk past value[39] and read adjacent stack memory until a stray quote byte is found or the index reaches len. The over-read string is then passed to strncmp()/atoi()/LOG_*, and if a quote byte is found out of bounds the subsequent value[p2] = '\0' performs a single-NUL out-of-bounds stack write at an attacker-influenced offset.

The %NOTIFYEV: payload carries network-derived content (LTIME network time, SIB1 base-station system information, CSPS/RRCSTATE), so a rogue cellular base station, a malicious or compromised modem module, or RF manipulation that induces an over-long notify line reaches the defect without any application interaction; the handler runs automatically on the unsolicited event in the modem RX thread.

The impact is out-of-bounds stack disclosure (into logs and parsing) and stack corruption that can crash the modem RX thread (denial of service). The write offset is only weakly controlled, so memory-safe code execution is not demonstrated. The fix bounds both scanning loops by out_len, keeping all accesses within the linearized buffer.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/12xxx/CVE-2026-12519.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-8hrc-q8cp-6xhf
- https://nvd.nist.gov/vuln/detail/CVE-2026-12519
- https://github.com/zephyrproject-rtos/zephyr/commit/c516cb7c14f8b0537811764daa94bedc50c230f3
- https://github.com/zephyrproject-rtos/zephyr
