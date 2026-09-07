# [M] Fat Free CRM vulnerable to Remote Denial of Service via Tasks endpoint

## Summary
Severity: Medium
Advisory: GHSA-p75c-5x3h-cxcg
CVE: CVE-2022-39281
CWE: CWE-20
Ecosystem: RubyGems
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-10-07
Source: https://github.com/advisories/GHSA-p75c-5x3h-cxcg
Type: github-advisory

## Affected
- RubyGems: `fat_free_crm` — affected >=0 <0.20.1

## Details
### Impact
An authenticated user can perform a remote Denial of Service attack against Fat Free CRM.

This vulnerability has been assigned the CVE identifier: CVE-2022-39281

Affected versions: All
Not affected: None
Fixed versions: 0.20.1

All users running an affected release should either upgrade or apply the patch immediately.

### Releases
Fixed versions: 0.20.1 and above

### Patches

If you are unable to upgrade immediately, you should apply the following patch.

```
diff --git a/app/models/polymorphic/task.rb b/app/models/polymorphic/task.rb
index d3d5c32c..7cdb24d6 100644
--- a/app/models/polymorphic/task.rb
+++ b/app/models/polymorphic/task.rb
@@ -189,6 +189,7 @@ class Task < ActiveRecord::Base
   #----------------------------------------------------------------------------
   def self.bucket_empty?(bucket, user, view = "pending")
     return false if bucket.blank? || !ALLOWED_VIEWS.include?(view)
+    return false unless Setting.task_bucket.map(&:to_s).include?(bucket.to_s)

     if view == "assigned"
       assigned_by(user).send(bucket).pending.count
```

### Credits

Thanks to @p- for reporting this and working with us to responsibly disclose this vulnerability.

### Further information
If you have any questions or comments about this advisory, please Open an issue in [GitHub Issue Tracker](https://github.com/fatfreecrm/fat_free_crm/issues)

## References
- https://github.com/fatfreecrm/fat_free_crm/security/advisories/GHSA-p75c-5x3h-cxcg
- https://nvd.nist.gov/vuln/detail/CVE-2022-39281
- https://github.com/fatfreecrm/fat_free_crm/commit/c85a2546348c2692d32f952c753f7f0b43d1ca71
- https://github.com/fatfreecrm/fat_free_crm
- https://github.com/fatfreecrm/fat_free_crm/releases/tag/v0.20.1
- https://github.com/rubysec/ruby-advisory-db/blob/master/gems/fat_free_crm/CVE-2022-39281.yml
