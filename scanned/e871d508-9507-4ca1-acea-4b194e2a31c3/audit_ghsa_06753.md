# [M] YesWiki: SQL injection via the `recentchanges` action `period` argument leads to arbitrary DB read

## Summary
Severity: Medium
Advisory: GHSA-89v6-j5x6-cmj3
CVE: CVE-2026-52763
CWE: CWE-1287, CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-09
Source: https://github.com/advisories/GHSA-89v6-j5x6-cmj3
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.6.6

## Details
### Summary

The `recentchanges` action (`actions/recentchanges.php`) accepts a `period` argument from two disjoint parameter spaces: the URL query string (`$_GET['period']`) and the action invocation `{{recentchanges period="..."}}`. A whitelist at line 17 validates only the URL form against `['day','week','month']`. The action-argument form takes the `else` branch at line 33 (`$dateMin = $this->GetParameter('period')`) with no validation, and the value flows into `PageManager::getRecentlyChanged()` (`includes/services/PageManager.php:196`), where it is interpolated into a `WHERE time >= '...' ORDER BY time DESC` clause without escaping or parameterization. UNION-based injection succeeds, the leaked rows render into the response page via `actions/recentchanges.php:43,58` (`ComposeLinkToPage($page['tag'])`), so any visitor of the trigger page sees the exfiltrated data.

The vulnerability provides arbitrary read of the YesWiki database to anyone who can save the trigger page. On a default install (`default_write_acl='*'`), this includes anonymous users, subject to the hashcash JS check on the page-edit form. Once the trigger page is saved, every subsequent view fires the injection as the SQLi is stored. Stored SQL injection is reachable through the page-edit flow, with arbitrary database read.

### Details

Two issues compose the vulnerability.

1. `actions/recentchanges.php` line 33 reads the action argument and skips the whitelist.

   ```php
   if (isset($_GET['period']) && in_array($_GET['period'], ['day', 'week', 'month'])) {
       switch ($_GET['period']) {
           case 'day':   $d = strtotime('-1 day');   $dateMin = date('Y-m-d H:i:s', $d); break;
           case 'week':  $d = strtotime('-1 week');  $dateMin = date('Y-m-d H:i:s', $d); break;
           case 'month': $d = strtotime('-1 month'); $dateMin = date('Y-m-d H:i:s', $d); break;
       }
   } else {
       $dateMin = $this->GetParameter('period');   
   }
   ```

   `Wiki::GetParameter()` (`includes/YesWiki.php:895`) reads `$this->parameter[$key]`, which is populated from the `{{action key=value}}` argument list — disjoint from `$_GET`. The whitelist's `if` branch only runs when `$_GET['period']` matches one of three exact values; in every other case the `else` branch reads the action argument with no validation, no escaping, no DateTime parse, no regex. The two parameter spaces are independent.

2.  In `includes/services/PageManager.php`, `PageManager::getRecentlyChanged()` interpolates the value into SQL.

   ```php
   public function getRecentlyChanged($limit = 50, $minDate = ''): ?array
   {
       if (!empty($minDate)) {
           if ($pages = $this->dbService->loadAll(
               'select id, tag, time, user, owner from' . $this->dbService->prefixTable('pages')
               . "where latest = 'Y' and comment_on = '' and time >= '$minDate' order by time desc"
           )) {
               return $pages;
           }
       }
   }
   ```

   `$minDate` is interpolated raw into the query and there is no `$this->dbService->escape($minDate)` and no parameter binding and no format check.

The default action ACL for `recentchanges` is `*` (`includes/YesWiki.php:1100`, `GetModuleACL`), so `Performer::CheckModuleACL('recentchanges', 'action')` returns `true` for everyone. The injection runs whenever a viewer reaches a page that embeds the action with a malicious `period` argument.

### PoC

Default fresh install so `default_write_acl='*'`.
1. place the SQLi payload on a page

```
{{recentchanges period="2000-01-01' UNION SELECT 9999 AS id, CONCAT('LEAK_', name, '_', SUBSTRING(password,1,32)) AS tag, NOW() AS time, name AS user, name AS owner FROM yeswiki_users WHERE name='AdminUser' -- "}}
```

The five UNION columns match the `id, tag, time, user, owner` projection that `getRecentlyChanged` selects. The `tag` column is rendered into the response as a hyperlink, exfiltrating the leaked data.

2. anyone visits the page

```http
GET /?<TriggerPage> HTTP/1.1
Host: target.example
```

The injected query executes server-side; the `tag` column is rendered into the page in `actions/recentchanges.php:43,58` via `ComposeLinkToPage($page['tag'])`.

### Impact

Arbitrary read of any DB column the application's MySQL user can access.

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-89v6-j5x6-cmj3
- https://github.com/YesWiki/yeswiki/commit/5da27474c3ee62270c8a6b9d7055d494cdbd38e5
- https://github.com/YesWiki/yeswiki
