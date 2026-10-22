# [H] Cloud Foundry denial of service vulnerability

## Summary
Severity: High
Advisory: GHSA-hxgw-7539-pv7r
CVE: CVE-2017-4960
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-05-13
Source: https://github.com/advisories/GHSA-hxgw-7539-pv7r
Type: github-advisory

## Affected
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=3.10.0 <3.12.0
- Maven: `org.cloudfoundry.identity:cloudfoundry-identity-server` — affected >=0 <3.9.8

## Details
An issue was discovered in Cloud Foundry release v247 through v252, UAA stand-alone release v3.9.0 through v3.11.0, and UAA Bosh Release v21 through v26. There is a potential to subject the UAA OAuth clients to a denial of service attack.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2017-4960
- https://github.com/cloudfoundry/uaa/commit/17a0b86afe1fbd4ed8819267906afa3f76a8dfdc
- https://github.com/cloudfoundry/uaa/commit/5eab756eaf4bb397302f00fbd0273f2470009d38
- https://github.com/cloudfoundry/uaa/commit/78731f8aa37a53385d0194821a5356ab66e2138
- https://github.com/cloudfoundry/uaa
- https://web.archive.org/web/20200227185243/http://www.securityfocus.com/bid/96780
- https://www.cloudfoundry.org/cve-2017-4960
