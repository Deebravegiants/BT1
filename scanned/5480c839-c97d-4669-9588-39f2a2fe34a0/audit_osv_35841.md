# [M] Type confusion in Zephyr HL78xx GNSS NMEA driver causes wild-pointer write from GNSS input

## Summary
Severity: Medium
Advisory: CVE-2026-15461
Aliases: GHSA-vvjg-6rg4-7235
CVSS: 5.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2026-09-10
Source: https://osv.dev/vulnerability/CVE-2026-15461
Type: osv

## Details
The Sierra Wireless HL78xx modem GNSS driver (drivers/modem/hl78xx/, later drivers/modem/vendor_standalone/hl78xx/) embeds a generic struct gnss_nmea0183_match_data match_data inside struct hl78xx_gnss_data. The generic NMEA0183 match helper (drivers/gnss/gnss_nmea0183_match.c) requires that context to be the first member because its callbacks cast user_data directly to struct gnss_nmea0183_match_data . In the affected releases match_data was the second member (after const struct device dev), so it sat at a non-zero offset while gnss_nmea0183_match_init() initialized it at the correct address. The registered NMEA handlers instead pass the whole device data object (data->devices.gnss->data, offset 0), producing an offset-shifted type confusion between where state is initialized and where the parse callbacks read and write it.

When NMEA sentences from the GNSS receiver are parsed, the GGA/RMC callbacks write parsed fix data into the wrong location within the struct, and the GSV callback (gnss_nmea0183_match_gsv_callback, active under CONFIG_GNSS_SATELLITES) reads its satellites pointer and bound from the wrong offsets — non-pointer bytes of struct hl78xx_gnss_data — and then writes parsed struct gnss_satellite entries through that bogus pointer. This is a write through an uninitialized/wild pointer with a garbage bound.

The NMEA handlers are registered by default (CONFIG_HL78XX_GNSS_SOURCE_NMEA is the default GNSS source) on devices using the HL78xx GNSS. The driver runs in kernel context and the NMEA data originates from the GNSS radio front-end, so a party able to influence the GNSS signal (for example GNSS/GPS spoofing at radio proximity) can drive the kernel-side parser into the faulty write. The most likely impact is a crash (denial of service) because the bogus pointer resolves to a fixed near-NULL value, with adjacent-memory corruption possible on MMU-less targets. Confidentiality is not affected. Exploitation requires the satellites feature to be enabled and active, so attack complexity is high.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/15xxx/CVE-2026-15461.json
- https://github.com/zephyrproject-rtos/zephyr/security/advisories/GHSA-vvjg-6rg4-7235
- https://nvd.nist.gov/vuln/detail/CVE-2026-15461
- https://github.com/zephyrproject-rtos/zephyr/commit/8a2465784e8909aa3835559381a60c00cc2218a1
- https://github.com/zephyrproject-rtos/zephyr
