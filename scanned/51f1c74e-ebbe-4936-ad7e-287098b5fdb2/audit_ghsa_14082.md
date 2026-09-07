# [M] Craft CMS stored XSS in review volume

## Summary
Severity: Medium
Advisory: GHSA-cjmm-x9x9-m2w5
CVE: CVE-2023-33196
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-05-26
Source: https://github.com/advisories/GHSA-cjmm-x9x9-m2w5
Type: github-advisory

## Affected
- Packagist: `craftcms/cms` — affected >=4.0.0-RC1 <4.4.7

## Details
### Summary
XSS can be triggered by review volumes

### PoC

    1. Access setting tab
    2. Create new assets
    3. In assets name inject payload: "<script>alert(1337)</script>
    4. Click Utilities tab
    5. Choose all volumes, or volume trigger xss
    6. Click Update asset indexes.
    7. Wait to assets update success.
    8. Progress complete.
    9. Click on review button will trigger XSS

### Root cause
Function: index.php?p=admin/actions/asset-indexes/process-indexing-session&v=1680710595770
After loading completed, progess will load: 
"skippedEntries"
and
"missingEntries"
These parameters is not yet filtered, I just tried "skippedEntries" but I think it will be work with "missingEntries"

### My reponse:
{
  "session": {
    "id": 10,
    "indexedVolumes": {
      "6": "\"<script>alert(1337)</script>"
    },
    "totalEntries": 2235,
    "processedEntries": 2235,
    "cacheRemoteImages": true,
    "listEmptyFolders": false,
    "isCli": false,
    "actionRequired": true,
    "dateCreated": "Apr 5, 2023, 9:03:16 AM",
    "skippedEntries": [
      "\"<script>alert(1337)</script>/assetpreviews/Image.php",
      "\"<script>alert(1337)</script>/assetpreviews/Pdf.php"
    ],
    "missingEntries": {
      "folders": [],
      "files": []
    },
    "processIfRootEmpty": false
  },
  "skipDialog": false
}



Resolved in https://github.com/craftcms/cms/commit/053d7119697e480ff81c5723bb9a33eaa49e0fc7

## References
- https://github.com/craftcms/cms/security/advisories/GHSA-cjmm-x9x9-m2w5
- https://nvd.nist.gov/vuln/detail/CVE-2023-33196
- https://github.com/craftcms/cms/commit/053d7119697e480ff81c5723bb9a33eaa49e0fc7
- https://github.com/craftcms/cms
- https://github.com/craftcms/cms/releases/tag/4.4.7
