# [M] Craft CMS vulnerable to Server-Side Request Forgery (SSRF) via GraphQL Asset Upload Mutation

## Summary
Severity: Medium
Advisory: GHSA-x27p-wfqw-hfcc
CVE: CVE-2025-68437
CWE: CWE-918
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:H/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-01-05
Source: https://github.com/advisories/GHSA-x27p-wfqw-hfcc
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.8.21
- Packagist: `craftcms/cms` — affected >=3.5.0 <4.16.17

## Details
The Craft CMS GraphQL `save_<VolumeName>_Asset` mutation is vulnerable to Server-Side Request Forgery (SSRF). This vulnerability arises because the `_file` input, specifically its `url` parameter, allows the server to fetch content from arbitrary remote locations without proper validation. Attackers can exploit this by providing internal IP addresses or cloud metadata endpoints as the `url`, forcing the server to make requests to these restricted services. The fetched content is then saved as an asset, which can subsequently be accessed and exfiltrated, leading to potential data exposure and infrastructure compromise. This exploitation requires specific GraphQL permissions for asset management within the targeted volume.

Users should update to the patched 5.8.21 and 4.16.17 releases to mitigate the issue.

References:

https://github.com/craftcms/cms/commit/013db636fdb38f3ce5657fd196b6d952f98ebc52

https://github.com/craftcms/cms/blob/5.x/CHANGELOG.md#5821---2025-12-04

---

### Required Permissions

The exploitation requires a few permissions to be enabled in the used GraphQL schema:
- "Edit assets in the `<VolumeName>` volume"
- "Create assets in the `<VolumeName>` volume"

### Steps to Reproduce

1. Log in to the Craft CMS control panel as an admin.

2. Create a new volume if you haven’t yet.

3. Create a new schema (or use the full/public schema) and enable the permissions mentioned above in the **Required Permissions** section.

4. Go to **GraphiQL**: `http://craft.local/admin/graphiql` & set the created schema.

5. Run the following GraphQL mutation to upload an Asset *(Replace the `<VolumeName>` with your volume name)*:

```graphql
mutation {
    save_<VolumeName>_Asset(_file: { 
        url: "http://127.0.0.1:80/index.php"
        filename: "poc.txt"
    }) {
        id
    }
}
```

6. Note that the `index.php` response will be saved as `poc.txt` & its content will be accessible via the asset preview/download functionality.

8. For the PoC, `http://127.0.0.1:80/index.php` was used as an example. However, the `url` parameter can be leveraged to target internal services, cloud metadata endpoints, or any arbitrary external URL.

## Impact

Successful exploitation of this SSRF vulnerability allows attackers to access internal network resources, bypass firewall rules, and conduct network reconnaissance.

In cloud environments (AWS, GCP, Azure), this can lead to the theft of sensitive credentials (e.g., IAM roles, service account tokens) from metadata endpoints, potentially resulting in the full compromise of the underlying infrastructure and the exfiltration of sensitive data.

---

Users should update to the patched versions (5.8.21 and 4.16.17) to mitigate the issue.

Users running Craft 3.5.0+ should update to the latest Craft 4.16.17 or 5.8.21 releases.

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-x27p-wfqw-hfcc
- https://nvd.nist.gov/vuln/detail/CVE-2025-68437
- https://github.com/craftcms/cms/commit/013db636fdb38f3ce5657fd196b6d952f98ebc52
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/blob/5.x/CHANGELOG.md#5821---2025-12-04
