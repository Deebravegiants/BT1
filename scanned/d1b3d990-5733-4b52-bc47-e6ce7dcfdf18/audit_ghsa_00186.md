# [H] Missing Regex anchor in Rack-Cors allows malicious third party site to perform CORS request

## Summary
Severity: High
Advisory: GHSA-2j9c-9vmv-7m39
CVE: CVE-2017-11173
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2018-07-31
Source: https://github.com/advisories/GHSA-2j9c-9vmv-7m39
Type: github-advisory

## Affected
- RubyGems: `rack-cors` — affected >=0 <0.4.1

## Details
Missing anchor in generated regex for rack-cors before 0.4.1 allows a malicious third-party site to perform CORS requests. If the configuration were intended to allow only the trusted `example.com` domain name and not the malicious `example.net` domain name, then `example.com.example.net` (as well as `example.com-example.net`) would be inadvertently allowed.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-11173
- https://github.com/cyu/rack-cors/commit/42ebe6caa8e85ffa9c8a171bda668ba1acc7a5e6
- https://github.com/cyu/rack-cors
- https://packetstormsecurity.com/files/143345/rack-cors-Missing-Anchor.html
- http://seclists.org/fulldisclosure/2017/Jul/22
- http://www.debian.org/security/2017/dsa-3931
