# [H] No rate limits on POST /uploads endpoint in Discourse

## Summary
Severity: High
Advisory: BIT-discourse-2024-24827
Aliases: CVE-2024-24827, GHSA-58vw-246g-fjj4
Ecosystem: Bitnami
Published: 2024-04-01
Source: https://osv.dev/vulnerability/BIT-discourse-2024-24827
Type: osv

## Affected
- Bitnami: `discourse` — affected >=0 <3.2.1

## Details
Discourse is an open source platform for community discussion. Without a rate limit on the POST /uploads endpoint, it makes it easier for an attacker to carry out a DoS attack on the server since creating an upload can be a resource intensive process. Do note that the impact varies from site to site as various site settings like `max_image_size_kb`, `max_attachment_size_kb` and `max_image_megapixels` will determine the amount of resources used when creating an upload. The issue is patched in the latest stable, beta and tests-passed version of Discourse. Users are advised to upgrade. Users unable to upgrade should reduce `max_image_size_kb`, `max_attachment_size_kb` and `max_image_megapixels` as smaller uploads require less resources to process. Alternatively, `client_max_body_size` can be reduced in Nginx to prevent large uploads from reaching the server.

## References
- https://github.com/discourse/discourse/commit/003b80e62f97cd8c0114d6b9d3f93c10443e6fae
- https://github.com/discourse/discourse/security/advisories/GHSA-58vw-246g-fjj4
- https://nvd.nist.gov/vuln/detail/CVE-2024-24827
