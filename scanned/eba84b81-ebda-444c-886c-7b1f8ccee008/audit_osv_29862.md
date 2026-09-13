# [H] Unaligned memory access in RPL option processing in Contiki-NG

## Summary
Severity: High
Advisory: CVE-2024-47181
Aliases: GHSA-crjw-x84h-h6x3
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-11-27
Source: https://osv.dev/vulnerability/CVE-2024-47181
Type: osv

## Details
Contiki-NG is an open-source, cross-platform operating system for IoT devices. An unaligned memory access can be triggered in the two RPL implementations of the Contiki-NG operating system. The problem can occur when either one of these RPL implementations is enabled and connected to an RPL instance. If an IPv6 packet containing an odd number of padded bytes before the RPL option, it can cause the rpl_ext_header_hbh_update function to read a 16-bit integer from an odd address. The impact of this unaligned read is architecture-dependent, but can potentially cause the system to crash. The problem has not been patched as of release 4.9, but will be included in the next release. One can apply the changes in Contiki-NG pull request #2962 to patch the system or wait for the next release.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/47xxx/CVE-2024-47181.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-crjw-x84h-h6x3
- https://nvd.nist.gov/vuln/detail/CVE-2024-47181
- https://github.com/contiki-ng/contiki-ng/pull/2962
