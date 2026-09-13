# [H] Out-of-bounds read in SNMP when decoding a string in Contiki-NG

## Summary
Severity: High
Advisory: CVE-2024-41125
Aliases: GHSA-qjj3-gqx7-438w
CVSS: 8.3 (CVSS:3.1/AV:A/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-11-27
Source: https://osv.dev/vulnerability/CVE-2024-41125
Type: osv

## Details
Contiki-NG is an open-source, cross-platform operating system for IoT devices. An out-of-bounds read of 1 byte can be triggered when sending a packet to a device running the Contiki-NG operating system with SNMP enabled. The SNMP module is disabled in the default Contiki-NG configuration. The vulnerability exists in the os/net/app-layer/snmp/snmp-ber.c module, where the function snmp_ber_decode_string_len_buffer decodes the string length from a received SNMP packet. In one place, one byte is read from the buffer, without checking that the buffer has another byte available, leading to a possible out-of-bounds read. The problem has been patched in Contiki-NG pull request #2936. It will be included in the next release of Contiki-NG. Users are advised to apply the patch manually or to wait for the next release. A workaround is to disable the SNMP module in the Contiki-NG build configuration.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/41xxx/CVE-2024-41125.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-qjj3-gqx7-438w
- https://nvd.nist.gov/vuln/detail/CVE-2024-41125
- https://github.com/contiki-ng/contiki-ng/pull/2936
