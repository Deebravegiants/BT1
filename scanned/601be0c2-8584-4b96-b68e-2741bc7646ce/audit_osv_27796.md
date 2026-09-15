# [M] Possible DoS Vulnerability with Range Header in Rack

## Summary
Severity: Medium
Advisory: CVE-2024-26141
Aliases: GHSA-xj5v-6v4g-jfw6
CVSS: 5.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:L)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2024-26141
Type: osv

## Details
Rack is a modular Ruby web server interface. Carefully crafted Range headers can cause a server to respond with an unexpectedly large response. Responding with such large responses could lead to a denial of service issue. Vulnerable applications will use the `Rack::File` middleware or the `Rack::Utils.byte_ranges` methods (this includes Rails applications). The vulnerability is fixed in 3.0.9.1 and 2.2.8.1.

## References
- https://discuss.rubyonrails.org/t/possible-dos-vulnerability-with-range-header-in-rack/84944
- https://lists.debian.org/debian-lts-announce/2024/04/msg00022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26141.json
- https://github.com/rack/rack/security/advisories/GHSA-xj5v-6v4g-jfw6
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2024-26141.yml
- https://nvd.nist.gov/vuln/detail/CVE-2024-26141
- https://security.netapp.com/advisory/ntap-20240510-0007/
- https://github.com/rack/rack/commit/4849132bef471adb21131980df745f4bb84de2d9
- https://github.com/rack/rack/commit/62457686b26d33a15a254c7768c2076e8e02b48b
