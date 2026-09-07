# [M] phpMyFAQ vulnerable to stored XSS on attachments filename

## Summary
Severity: Medium
Advisory: GHSA-7m8g-fprr-47fx
CVE: CVE-2024-24574
CWE: CWE-79, CWE-80
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:L (CVSS_V3)
Published: 2024-02-05
Source: https://github.com/advisories/GHSA-7m8g-fprr-47fx
Type: github-advisory

## Affected
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <3.2.5

## Details
### Summary
Unsafe echo of filename in phpMyFAQ\phpmyfaq\admin\attachments.php leading to allow execute JavaScript code in client side (XSS)

### Details
On that snippet code of rendering the file attachments from user tables

```
<?php foreach ($crumbs as $item) : ?>
        <tr id="attachment_<?= $item->id ?>" title="<?= $item->thema ?>">
          <td><?= $item->id ?></td>
          <td><?= $item->filename ?></td>
          <td><?= $item->record_lang ?></td>
          <td><?= Utils::formatBytes($item->filesize) ?></td>
          <td><?= $item->mime_type ?></td>
          <td>
```

The data directly rendering with short hand echo without any sanitation first, its recommend to use  existing class of `Strings::htmlentities` on use `phpMyFAQ\Strings;`

```
<td><?= Strings::htmlentities($item->filename); ?></td>
<td><?= Strings::htmlentities($item->record_lang); ?></td>
<td><?= Utils::formatBytes($item->filesize) ?></td>
<td><?= Strings::htmlentities($item->mime_type); ?></td>
```

Propose fixing on that pull request https://github.com/thorsten/phpMyFAQ/pull/2827

### PoC
1. An attacker with permission will upload the attachments image on [http://{base_url}/admin/?action=editentry](http://{base_url}/admin/?action=editentry)
2. On endpoint of ajax upload image POST /admin/index.php?action=ajax&ajax=att&ajaxaction=upload 
3. Change the originally name file on parameters  filename to a XSS payload 
4. The XSS will trigger on attachment pages /admin/?action=attachments

- Trigger XSS
![image](https://user-images.githubusercontent.com/37658579/301022211-81da265b-5dce-48bd-a043-8bae0991fe46.png)

- Payload XSS
<img width="1000" alt="image" src="https://user-images.githubusercontent.com/37658579/301022571-d6cdd166-b1f9-4062-87c5-c8bbb308cd5d.png">




### Impact

This vulnerability will allow an attacker with a permissions of uploading an attachment to storing the payload of XSS on database specific table `faqattachment` columns `filename.`

The XSS payload could be rendering on page that listing the file on tables, and impact to others user that on the hierarchy. 

The payload XSS have several attack scenario such like 

1. Stealing the cookies (isn’t possible since HttpOnly)
2. Crashing the application with a looping javascript payload

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-7m8g-fprr-47fx
- https://nvd.nist.gov/vuln/detail/CVE-2024-24574
- https://github.com/thorsten/phpMyFAQ/pull/2827
- https://github.com/thorsten/phpMyFAQ/commit/5479b4a4603cce71aa7eb4437f1c201153a1f1f5
- https://github.com/thorsten/phpMyFAQ
- https://www.phpmyfaq.de/security/advisory-2024-02-05
