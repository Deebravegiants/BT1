# [H] CVE-2017-14388

## Summary
Severity: High
Advisory: CVE-2017-14388
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2017-11-13
Source: https://osv.dev/vulnerability/CVE-2017-14388
Type: osv

## Details
Cloud Foundry Foundation GrootFS release 0.3.x versions prior to 0.30.0 do not validate DiffIDs, allowing specially crafted images to poison the grootfs volume cache. For example, this could allow an attacker to provide an image layer that GrootFS would consider to be the Ubuntu base layer.

## References
- https://www.cloudfoundry.org/cve-2017-14388/
