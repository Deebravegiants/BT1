# [M] phpMyFAQ is Vulnerable to Stored XSS via Unsanitized Email Field in Admin FAQ Editor

## Summary
Severity: Medium
Advisory: GHSA-98gw-w575-h2ph
CVE: CVE-2026-32629
CWE: CWE-20, CWE-79
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:N/VI:N/VA:N/SC:H/SI:H/SA:N/E:P (CVSS_V4)
Published: 2026-03-31
Source: https://github.com/advisories/GHSA-98gw-w575-h2ph
Type: github-advisory

## Affected
- Packagist: `thorsten/phpmyfaq` — affected >=0 <4.1.1
- Packagist: `phpmyfaq/phpmyfaq` — affected >=0 <4.1.1

## Details
### Summary
An unauthenticated attacker can submit a guest FAQ with an email address that is syntactically valid per RFC 5321 (quoted local part) yet contains raw HTML — for example "<script>alert(1)</script>"@evil.com. PHP's FILTER_VALIDATE_EMAIL accepts this email as valid. The email is stored in the database without HTML sanitization and later rendered in the admin FAQ editor template using Twig's |raw filter, which bypasses auto-escaping entirely.

### Details
1. PHP FILTER_VALIDATE_EMAIL accepts RFC-valid quoted local parts with dangerous characters

phpmyfaq/src/phpMyFAQ/Controller/Frontend/Api/FaqController.php:99
$email = trim((string) Filter::filterVar($data->email, FILTER_VALIDATE_EMAIL));
PHP accepts "<script>alert(1)</script>"@evil.com as a valid email (RFC 5321 allows <, > inside quoted local parts). Confirmed:
"<script>alert(1)</script>"@evil.com => string (valid, not false)

2. Email stored raw without HTML sanitization

phpmyfaq/src/phpMyFAQ/Faq.php — email retrieved directly as $row->email from the database.

3. Admin Twig template renders email with |raw

phpmyfaq/assets/templates/admin/content/faq.editor.twig:296
<input type="email" name="email" id="email" value="{{ faqData['email'] | raw }}" class="form-control">

Affected version: 4.2.0-alpha, commit f0dc86c8f


### PoC
**The reproduction of the vulnerability was implemented with the help of AI while reviewing the source code to generate the proof-of-concept. Please kindly note this for reference. Since the vulnerability has already been confirmed directly in the source code, the proof-of-concept code may be considered as a reference only.**

Please extract the attached compressed file and proceed.
[poc.zip](https://github.com/user-attachments/files/25938058/poc.zip)


0. (docker compose -f docker-compose.yml down -v)
1. docker compose -f docker-compose.yml up -d mariadb php-fpm nginx
2. bash exploit.sh
-----
1. Access http://localhost:8888/admin/
2. Log in with admin / Admin1234!
3. After logging in, check whether the URL remains http://localhost:8888/admin/
4. Go to Content → FAQ Administration → edit "poc" → alert popup should appear
If it does not appear, you can also access it directly via:
http://localhost:8888/admin/faq/edit/1/en


<img width="1388" height="239" alt="스크린샷 2026-03-12 오후 11 42 52" src="https://github.com/user-attachments/assets/b6d5446f-4eba-4cb2-9284-1bca4855142e" />
<img width="1171" height="92" alt="스크린샷 2026-03-12 오후 11 16 17" src="https://github.com/user-attachments/assets/3578e429-7106-4616-92ed-4167816d40f0" />


### Impact
When an administrator opens /admin/faq/edit/{id}/{lang} to review the pending FAQ, the injected script executes in the admin's browser context. This allows an attacker to:

- Steal the administrator's session cookie → full admin account takeover
- Perform arbitrary admin actions (create users, modify content, change configuration)
- Pivot to further attacks on the server

The attack chain requires no authentication. By default, records.allowNewFaqsForGuests=true allows unauthenticated FAQ submission, and records.defaultActivation=false guarantees the administrator must visit the edit page to review it.

Note on captcha: The built-in captcha is enabled by default when the PHP gd extension is present (spam.enableCaptchaCode=true). This prevents fully automated exploitation but does not prevent a targeted manual attack — an attacker can solve the captcha once and submit the payload. 

### Credits
wooseokdotkim

## References
- https://github.com/thorsten/phpMyFAQ/security/advisories/GHSA-98gw-w575-h2ph
- https://nvd.nist.gov/vuln/detail/CVE-2026-32629
- https://github.com/thorsten/phpMyFAQ
- https://github.com/thorsten/phpMyFAQ/releases/tag/4.1.1
