# [C] Untrusted Deserialization in ClipBucket-v5 Version 2.0 to 5.5.1 Revision 199

## Summary
Severity: Critical
Advisory: CVE-2024-54135
Aliases: GHSA-4523-mqmv-wrqx
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-12-06
Source: https://osv.dev/vulnerability/CVE-2024-54135
Type: osv

## Details
ClipBucket V5 provides open source video hosting with PHP. ClipBucket-v5 Version 2.0 to Version 5.5.1 Revision 199 are vulnerable to PHP Deserialization vulnerability. The vulnerability exists in upload/photo_upload.php  within the decode_key function. User inputs were supplied to this function without sanitization via collection GET parameter and photoIDS POST parameter respectively. The decode_key function invokes PHP unserialize function as defined in upload/includes/classes/photos.class.php. As a result, it is possible for an adversary to inject maliciously crafted PHP serialized object and utilize gadget chains to cause unexpected behaviors of the application. This vulnerability is fixed in 5.5.1 Revision 200.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/54xxx/CVE-2024-54135.json
- https://github.com/MacWarrior/clipbucket-v5/security/advisories/GHSA-4523-mqmv-wrqx
- https://nvd.nist.gov/vuln/detail/CVE-2024-54135
- https://github.com/MacWarrior/clipbucket-v5/commit/76a829c088f0813ab3244a3bd0036111017409b0
