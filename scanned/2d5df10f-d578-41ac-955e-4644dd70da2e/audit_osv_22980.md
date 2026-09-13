# [M] Out-of-bounds read and write in BLE L2CAP module

## Summary
Severity: Medium
Advisory: CVE-2022-41873
Aliases: GHSA-m5cj-fw8m-ffgf
CVSS: 4.2 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N)
Published: 2022-11-11
Source: https://osv.dev/vulnerability/CVE-2022-41873
Type: osv

## Details
Contiki-NG is an open-source, cross-platform operating system for Next-Generation IoT devices. Versions prior to 4.9 are vulnerable to an Out-of-bounds read. While processing the L2CAP protocol, the Bluetooth Low Energy stack of Contiki-NG needs to map an incoming channel ID to its metadata structure. While looking up the corresponding channel structure in get_channel_for_cid (in os/net/mac/ble/ble-l2cap.c), a bounds check is performed on the incoming channel ID, which is meant to ensure that the channel ID does not exceed the maximum number of supported channels.However, an integer truncation issue leads to only the lowest byte of the channel ID to be checked, which leads to an incomplete out-of-bounds check. A crafted channel ID leads to out-of-bounds memory to be read and written with attacker-controlled data. The vulnerability has been patched in the "develop" branch of Contiki-NG, and will be included in release 4.9. As a workaround, Users can apply the patch in Contiki-NG pull request 2081 on GitHub.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/41xxx/CVE-2022-41873.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-m5cj-fw8m-ffgf
- https://nvd.nist.gov/vuln/detail/CVE-2022-41873
- https://github.com/contiki-ng/contiki-ng/pull/2081
