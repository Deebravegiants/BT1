# [M] phpIPAM Temporary Subnet Share Information Disclosure via Address Parameter

## Summary
Severity: Medium
Advisory: CVE-2026-75105
CVSS: 6.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-17
Source: https://osv.dev/vulnerability/CVE-2026-75105
Type: osv

## Details
phpIPAM through 1.8.1 fails to verify that a requested IP address belongs to the subnet a temporary share token was issued for. In app/temp_share/index.php and app/temp_share/address.php, when the share type is 'subnets', the subnetId parameter is used directly as a database primary key to fetch an address without confirming the address belongs to the authorized subnet. An unauthenticated party holding any valid, non-expired temporary share URL can enumerate the subnetId parameter to read every IP address record across all sections and subnets, including hostnames, DNS names, MAC addresses, owner/contact fields, and notes (which may contain credentials and configuration details).

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/75xxx/CVE-2026-75105.json
- https://github.com/phpipam/phpipam/releases/tag/v1.8.2
- https://nvd.nist.gov/vuln/detail/CVE-2026-75105
- https://www.vulncheck.com/advisories/phpipam-temporary-subnet-share-information-disclosure-via-address-parameter
- https://github.com/phpipam/phpipam/issues/4623
- https://github.com/phpipam/phpipam/commit/2980be03652c0eb1db9fe2bcefaa210c854b9aea
- https://github.com/phpipam/phpipam
