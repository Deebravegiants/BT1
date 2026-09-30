# [M] Possible Denial of Service Vulnerability in Rack Header Parsing

## Summary
Severity: Medium
Advisory: CVE-2024-26146
Aliases: GHSA-54rr-7fvw-6x8f
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-02-28
Source: https://osv.dev/vulnerability/CVE-2024-26146
Type: osv

## Details
Rack is a modular Ruby web server interface. Carefully crafted headers can cause header parsing in Rack to take longer than expected resulting in a possible denial of service issue. Accept and Forwarded headers are impacted. Ruby 3.2 has mitigations for this problem, so Rack applications using Ruby 3.2 or newer are unaffected. This vulnerability is fixed in 2.0.9.4, 2.1.4.4, 2.2.8.1, and 3.0.9.1.

## References
- https://discuss.rubyonrails.org/t/possible-denial-of-service-vulnerability-in-rack-header-parsing/84942
- https://lists.debian.org/debian-lts-announce/2024/04/msg00022.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/26xxx/CVE-2024-26146.json
- https://github.com/rack/rack/security/advisories/GHSA-54rr-7fvw-6x8f
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/rack/CVE-2024-26146.yml
- https://nvd.nist.gov/vuln/detail/CVE-2024-26146
- https://security.netapp.com/advisory/ntap-20240510-0006/
- https://github.com/rack/rack/commit/30b8e39a578b25d4bdcc082c1c52c6f164b59716
- https://github.com/rack/rack/commit/6c5d90bdcec0949f7ba06db62fb740dab394b582
- https://github.com/rack/rack/commit/a227cd793778c7c3a827d32808058571569cda6f
- https://github.com/rack/rack/commit/e4c117749ba24a66f8ec5a08eddf68deeb425ccd
