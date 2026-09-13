# [M] Decidim: Veriﬁcation admins can access supplied IDs from other organizations

## Summary
Severity: Medium
Advisory: GHSA-86fh-w43w-338c
CVE: CVE-2026-45330
CWE: CWE-200
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-13
Source: https://github.com/advisories/GHSA-86fh-w43w-338c
Type: github-advisory

## Affected
- RubyGems: `decidim-verifications` — affected >=0 <0.30.9
- RubyGems: `decidim-verifications` — affected >=0.31.0.rc1 <0.31.5
- RubyGems: `decidim-verifications` — affected >=0.32.0.rc1 <0.32.0

## Details
## Description

The verification admin mutation flow allows accessing, verifying, and rejecting participants records from another tenant.

## Technical description

The verification admin controllers loads pending_authorization_id with a raw `Authorization.find(...)` and then authorizes the record without checking whether it belongs to current_organization.

Reproduction steps:

1. An org2 participant uploads their ID:

<img width="2184" height="1288" alt="decidim-verification-01" src="https://github.com/user-attachments/assets/c6713454-c787-4795-b852-3c2c672358d6" />

2. An admin from another organisation, in this case org1, is able to open the ID from org2 by opening request 35, e.g `http://localhost:3001/admin/id_documents/pending_authorizations/35/confirmations/new`

<img width="1539" height="1037" alt="decidim-verification-02" src="https://github.com/user-attachments/assets/6ed646de-a501-4964-8467-013ada55ce2d" />

3. The admin then approves this request by looking up the ID in the picture (not shown in this image, but a real ID would expose this)
 
<img width="1542" height="652" alt="decidim-verification-03" src="https://github.com/user-attachments/assets/c7ee5bea-3fa2-43d9-8330-8d834f34a9af" />

4. Now the request has been approved, which can be seen from the org2 participant authorizations page:

<img width="2279" height="720" alt="decidim-verification-04" src="https://github.com/user-attachments/assets/55ee1bab-d396-4e0f-803f-21dc31a2c125" />

### Impact

A tenant admin can access, reject or approve another tenant's `id_documents` requests.

### Patches

See https://github.com/decidim/decidim/pull/16666

### Workarounds

Disable the "Identity documents" verification 

### Reference

OWASP A01:2021 Broken Access Control

### Credits

This issue was discovered in a security audit organized by the [Decidim Association](https://decidim.org) and made by [Radically Open Security](https://www.radicallyopensecurity.com/) against Decidim financed by [NGI](https://ngi.eu/).

## References
- https://github.com/decidim/decidim/security/advisories/GHSA-86fh-w43w-338c
- https://github.com/decidim/decidim/pull/16666
- https://github.com/decidim/decidim
