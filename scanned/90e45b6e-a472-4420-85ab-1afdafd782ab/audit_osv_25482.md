# [M] Out-of-bounds read during IPHC address decompression

## Summary
Severity: Medium
Advisory: CVE-2023-37281
Aliases: GHSA-2v4c-9p48-g9pr
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-09-15
Source: https://osv.dev/vulnerability/CVE-2023-37281
Type: osv

## Details
Contiki-NG is an operating system for internet-of-things devices. In versions 4.9 and prior, when processing the various IPv6 header fields during IPHC header decompression, Contiki-NG confirms the received packet buffer contains enough data as needed for that field. But no similar check is done before decompressing the IPv6 address. Therefore, up to 16 bytes can be read out of bounds on the line with the statement `memcpy(&ipaddr->u8[16 - postcount], iphc_ptr, postcount);`. The value of `postcount` depends on the address compression used in the received packet and can be controlled by the attacker. As a result, an attacker can inject a packet that causes an out-of-bound read. As of time of publication, a patched version is not available. As a workaround, one can apply the changes in Contiki-NG pull request #2509 to patch the system.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/37xxx/CVE-2023-37281.json
- https://github.com/contiki-ng/contiki-ng/security/advisories/GHSA-2v4c-9p48-g9pr
- https://nvd.nist.gov/vuln/detail/CVE-2023-37281
- https://github.com/contiki-ng/contiki-ng/pull/2509
