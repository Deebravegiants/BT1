# [M] WWBN AVideo: Stored XSS via unescaped Gallery category description

## Summary
Severity: Medium
Advisory: GHSA-c8h8-vq34-9fw2
CVE: CVE-2026-47694
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-04
Source: https://github.com/advisories/GHSA-c8h8-vq34-9fw2
Type: github-advisory

## Affected
- Packagist: `WWBN/AVideo` — affected >=0

## Details
### Summary

  AVideo stores category descriptions from user input and later renders `category_description` as raw HTML in the Gallery view. A user who can create or edit
categories can store JavaScript in a category description, which executes when another user views the affected Gallery/category page.

  This is a stored XSS in the category `description` field, separate from previously fixed XSS issues in video titles or comments.

  ### Details

  Source:

  `objects/categoryAddNew.json.php`

  ```php
  $objCat->setDescription($_POST['description']);

  Storage setter:

  objects/category.php

  public function setDescription($description)
  {
      $this->description = $description;
  }
```
  Sink:

  `plugin/Gallery/view/mainAreaCategory.php`
```
  <div id="categoryDescription<?php echo $duid; ?>" style="display: none;"><?php echo $videos[0]['category_description']; ?></div>
```
  The value is rendered without `htmlspecialchars()`, `htmlentities()`, `HTMLPurifier`, or equivalent output encoding.

  ### PoC

  Prerequisites:

  - AVideo current master / v29.0
  - User account with permission to create or edit categories
  - Gallery plugin/view enabled
  - At least one video assigned to the affected category

  Steps:

  1. Log in as a user who can create or edit categories.
  2. Create or edit a category.
  3. Set the category description to:
```
  <img src=x onerror=alert(document.domain)>
```
  4. Save the category.
  5. Assign at least one video to that category.
  6. Open the Gallery/category page that renders the category section.
  7. The payload is inserted into the page as raw HTML and JavaScript executes.

  ### Impact

  An attacker with category edit permission can execute JavaScript in the browser of users or administrators who view the affected Gallery/category page. This can
  be used to perform actions as the victim, steal same-origin data accessible to JavaScript, or abuse administrative UI actions if an administrator views the
  malicious category.

### Recommended fix

- Sanitize category descriptions on input with the same HTML policy used for video descriptions, or store plain text only.
- Encode on output:

```php
echo htmlspecialchars($videos[0]['category_description'], ENT_QUOTES, 'UTF-8');
```

- If limited HTML is intended, run the description through HTMLPurifier before storage or before render.
- Add regression tests for category description rendering in Gallery views.

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-c8h8-vq34-9fw2
- https://nvd.nist.gov/vuln/detail/CVE-2026-47694
- https://github.com/WWBN/AVideo/commit/6a6ff1f5bff1904f91f612db9f0da083295392b1
- https://github.com/WWBN/AVideo
