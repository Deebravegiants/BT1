# [M] EGroupware Vulnerable to Local File Inclusion via file:// URI in Mail Compose

## Summary
Severity: Medium
Advisory: GHSA-c8m7-r2jv-rw63
CVE: CVE-2026-45016
CWE: CWE-73
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-07
Source: https://github.com/advisories/GHSA-c8m7-r2jv-rw63
Type: github-advisory

## Affected
- Packagist: `egroupware/egroupware` — affected >=26.0.20251208 <26.5.20260507
- Packagist: `egroupware/egroupware` — affected >=0 <23.1.20260601

## Details
### Summary
The function processes image URLs embedded in an HTML email body without validating or restricting URI schemes. The check `!str_starts_with($myUrl, 'http')` evaluates to true for `file://` URIs, causing `file_get_contents($basedir . urldecode($myUrl))` to read arbitrary files from the server filesystem and embed them as inline MIME attachments in outgoing email.

str_starts_with('file:///etc/passwd', 'http') → **false**
!false → **true**


```php
// api/src/Mail.php  
foreach($images[2] as $i => $url)
			{
				//$isData = false;
				$basedir = $data = '';
				$needTempFile = true;
				$attachmentData = ['name' => '', 'type' => '', 'file' => '', 'tmp_name' => ''];
				try
				{
					// do not change urls for absolute images (thanks to corvuscorax)
					if (!str_starts_with($url, 'data:'))
					{
						$attachmentData['name'] = basename($url); // need to resolve all sort of url
						if (($directory = dirname($url)) == '.') $directory = '';
						$ext = pathinfo($attachmentData['name'], PATHINFO_EXTENSION);
						$attachmentData['type'] = MimeMagic::ext2mime($ext);
						if ( strlen($directory) > 1 && !str_ends_with($directory, '/')) { $directory .= '/'; }
..
...
....
// processURL2InlineImages function
if ( $myUrl[0]!='/' && strlen($basedir) > 1 && !str_ends_with($basedir, '/')) { $basedir .= '/'; }
						if ($needTempFile && empty($attachment) && !str_starts_with($myUrl, "http"))
						{
							try {
								$data = file_get_contents($basedir.urldecode($myUrl));
							}
							catch (\Throwable $e) {
								_egw_log_exception($e);
							}
						}
					}
					if (str_starts_with($url, 'data:'))
```

### PoC
1. Log in as any authenticated EGroupware user with mail access and open the mail compose window.
2. Switch to HTML body mode and insert: `<img src="file:///etc/passwd">`. 
3. The server executes file_get_contents('file:///etc/passwd'), writes the content to a temp file, and attaches it as an inline MIME part. 


### Impact
An authenticated attacker can read arbitrary files accessible by the web server process, including /etc/passwd, application configuration files containing database credentials, private TLS keys, and environment files.


### Remediation
Enforce a strict URI scheme allowlist before calling file_get_contents(). Replace the check `!str_starts_with($myUrl, 'http')` with `if (!preg_match('#^https?://#i', $myUrl)) { continue; }` to reject `file://`, `ftp://`, `php://`, `data://`, and any other non-HTTP scheme.

## References
- https://github.com/EGroupware/egroupware/security/advisories/GHSA-c8m7-r2jv-rw63
- https://github.com/EGroupware/egroupware
