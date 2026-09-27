# [H] Unverified DIO prefix info lengths in RPL-Classic in Contiki-NG

## Summary
Severity: High
Advisory: CVE-2022-35927
Aliases: GHSA-9rm9-3phh-p4wm
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-08-04
Source: https://osv.dev/vulnerability/CVE-2022-35927
Type: osv

## Details
Contiki-NG is an open-source, cross-platform operating system for IoT devices. In the RPL-Classic routing protocol implementation in the Contiki-NG operating system, an incoming DODAG Information Option (DIO) control message can contain a prefix information option with a length parameter. The value of the length parameter is not validated, however, and it is possible to cause a buffer overflow when copying the prefix in the set_ip_from_prefix function. This vulnerability affects anyone running a Contiki-NG version prior to 4.7 that can receive RPL DIO messages from external parties. To obtain a patched version, users should upgrade to Contiki-NG 4.7 or later. There are no workarounds for this issue.

## References
- https://github.com/contiki-ng/contiki-ng/pull/1589/commits/4fffab0e632c4d01910fa957d1fd9ef321eb87d2
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2022/35xxx/CVE-2022-35927.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-9rm9-3phh-p4wm
- https://nvd.nist.gov/vuln/detail/CVE-2022-35927
- https://github.com/contiki-ng/contiki-ng/pull/1589
