# [H] Cross-site scripting (XSS) from unsanitized uploaded SVG files in Kirby

## Summary
Severity: High
Advisory: GHSA-qgp4-5qx6-548g
CVE: CVE-2021-29460
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:L/A:N (CVSS_V3)
Published: 2021-04-30
Source: https://github.com/advisories/GHSA-qgp4-5qx6-548g
Type: github-advisory

## Affected
- Packagist: `getkirby/cms` — affected >=0 <3.5.4

## Details
### Impact

An editor with write access to the Kirby Panel can upload an SVG or XML file that contains harmful content like `<script>` tags. The direct link to that file can be sent to other users or visitors of the site. If the victim opens that link in a browser where they are logged in to Kirby, the script will run and can for example trigger requests to Kirby's API with the permissions of the victim.

This vulnerability is critical if you might have potential attackers in your group of authenticated Panel users. They can escalate their privileges if they get access to the Panel session of an admin user. Depending on your site, other JavaScript-powered attacks are possible.

Visitors without Panel access can only use this attack vector if your site allows SVG or XML file uploads in frontend forms and you don't already validate or sanitize uploaded SVG or XML files.

The attack requires user interaction by another user or visitor and *cannot* be automated.

### Patches

#### Uploads in the Panel

The problem has been patched in [Kirby 3.5.4](https://github.com/getkirby/kirby/releases/tag/3.5.4) by validating uploaded SVG and XML files and rejecting potentially harmful files. Please update to this or a [later version](https://github.com/getkirby/kirby/releases/) to fix the vulnerability.

#### Frontend upload forms

Frontend upload forms need to be patched separately depending on how they store the uploaded file(s). If you use `File::create()`, you are protected by updating to Kirby 3.5.4+.

#### Validate existing files

Already uploaded files are *not* automatically validated again. If you are not sure if you have been impacted by this vulnerability in the past, we recommend to run all site files through the validator classes after updating to Kirby 3.5.4. You can use the following test script by pasting it into a template or uploading it to your web root:

```php
<?php

@include_once __DIR__ . '/kirby/bootstrap.php';

if (version_compare(kirby()->version(), '3.5.4', '<') === true) {
  die('This script requires Kirby 3.5.4+.');
}

$objects = [
  // the site itself
  site(),

  // all pages and drafts
  ...site()->index(true)->values(),

  // all users
  ...kirby()->users()->values()
];

$errors = false;
foreach ($objects as $object) {
  foreach ($object->files() as $file) {
    try {
      // validate the contents lazily
      // (if a validator exists)
      $file->validateContents(true);
    } catch (\Kirby\Exception\InvalidArgumentException $e) {
      echo $file->id() . ': ' . $e->getMessage() . "<br>\n";
      $errors = true;
    }
  }
}

if ($errors === false) {
  echo 'No validation errors found.';
}
```

You only need to run this validator script once as future uploads will automatically be validated. If the script prints "No validation errors found", you have not been impacted by the vulnerability so far.

Errors that it lists may or may not be critical as our validator classes also catch files with an invalid data structure or less harmful attacks like the ["billion laughs" denial-of-service attack](https://en.wikipedia.org/wiki/Billion_laughs_attack) or the usage of external sources. We recommend to review and fix each listed error manually until the script no longer finds any validation errors.

**Please delete the script again after you have used it.**

### Workarounds

If you cannot update to Kirby 3.5.4, you can disable the upload of SVG and XML files in your [file blueprints](https://getkirby.com/docs/reference/panel/blueprints/file#accept) and validate or replace your already uploaded files once.

### Credits

Thanks to @sreenathr10 for reporting the problem.

## References
- https://github.com/getkirby/kirby/security/advisories/GHSA-qgp4-5qx6-548g
- https://nvd.nist.gov/vuln/detail/CVE-2021-29460
- https://github.com/getkirby/kirby/releases/tag/3.5.4
- http://packetstormsecurity.com/files/162359/Kirby-CMS-3.5.3.1-Cross-Site-Scripting.html
