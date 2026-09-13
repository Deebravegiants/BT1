# [H] CVE-2023-41102

## Summary
Severity: High
Advisory: CVE-2023-41102
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-11-17
Source: https://osv.dev/vulnerability/CVE-2023-41102
Type: osv

## Details
An issue was discovered in the captive portal in OpenNDS before version 10.1.3. It has multiple memory leaks due to not freeing up allocated memory. This may lead to a Denial-of-Service condition due to the consumption of all available memory. Affected OpenNDS before version 10.1.3 fixed in OpenWrt master and OpenWrt 23.05 on 23. November by updating OpenNDS to version 10.2.0.

## References
- https://github.com/openNDS/openNDS/releases/tag/v10.1.3
- https://source.sierrawireless.com/resources/security-bulletins/sierra-wireless-technical-bulletin---swi-psa-2023-006-v4/#sthash.2vJg3d85.rwx82g1C.dpbs
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2023/41xxx/CVE-2023-41102.json
- https://nvd.nist.gov/vuln/detail/CVE-2023-41102
- https://github.com/openNDS/openNDS/commit/31dbf4aa069c5bb39a7926d86036ce3b04312b51
- https://github.com/openwrt/routing/commit/ad787a920ccb9dacf5b01d52bce36ac14a5ecd89
