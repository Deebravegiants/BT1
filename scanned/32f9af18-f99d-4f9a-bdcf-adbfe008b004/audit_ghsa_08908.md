# [M] Admidio writes session IDs and auto-login cookie values to application logs

## Summary
Severity: Medium
Advisory: GHSA-mch8-wf3h-6x88
CVE: CVE-2026-47234
CWE: CWE-200, CWE-532
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-mch8-wf3h-6x88
Type: github-advisory

## Affected
- Packagist: `admidio/admidio` — affected >=0 <5.0.10

## Details
## Summary

When debug logging is enabled, `Session::setCookie()` logs full cookie values and `Session::start()` logs the current session ID. In a real Admidio deployment this includes both the active session cookie and the persistent auto-login cookie. Anyone with access to the log sink can recover live bearer-style credentials from the logs.

## Vulnerable Code Links

- https://github.com/Admidio/admidio/blob/v5.0.9/src/Session/Entity/Session.php#L533-L540
- https://github.com/Admidio/admidio/blob/v5.0.9/src/Session/Entity/Session.php#L615-L617

## Vulnerable Code

```php
// src/Session/Entity/Session.php
$gLogger->info('Set Cookie!', array(
'name' => $name,
'value' => $value,
'expire' => $expire,
'path' => $path,
'domain' => $domain,
'secure' => $secure,
'httpOnly' => $httpOnly,
'sameSite' => 'lax'
));
...
session_start();
$gLogger->info('Session Started!', array(
'name' => $sessionName,
'limit' => $limit,
'path' => $path,
'domain' => $domain,
'secure' => $secure,
'httpOnly' => $httpOnly,
'sameSite' => 'lax',
'sessionId' => session_id()
));
```


## What Does The Code Mean

Every time Admidio sets a cookie, it writes the raw cookie value to the application log. When a session starts, it writes the active session identifier too.

## Why The Code Is Vulnerable

Session IDs and persistent auto-login values are credentials. Logging them turns the log file into a credential store and expands the trust boundary to anyone who can read logs, backups, or external log aggregation outputs.

## Verification Environment

- Application: Admidio `v5.0.9`
- Runtime: Dockerized Admidio + MariaDB on `http://localhost:18080`
- Validation mode: real deployed application, not isolated unit tests

## Steps To Reproduce

1. Enable Admidio debug logging.
2. Log in with `auto_login=1` enabled.
3. Inspect the generated application log.
4. Observe that the log contains both the `ADMIDIO_*_AUTO_LOGIN_ID` value and the `ADMIDIO_*_SESSION_ID` value in cleartext.


## PoC Script

```python
from helpers import login, new_session, save_json


def main():
session = new_session()
result = login(session, "admin", "AdminPass123!", auto_login=True)
save_json("session_logging_login.json", result)


if __name__ == "__main__":
main()
```

## PoC Output

```text
{
  "cookies": {
"ADMIDIO_admidio_adm_AUTO_LOGIN_ID": "2%3AnO2BhCdRgFUMKT46e2EzS79Inf4oWiLWzLnX9Ko5",
"ADMIDIO_admidio_adm_SESSION_ID": "iga3ujr67cti6s7btnuhecte67"
  },
  "csrf": "y41CaDdEO7RKug5FIRWO2Dx8w7KVQZ",
  "json": {
"status": "success",
"url": "http://localhost:18080/modules/overview.php"
  },
  "status_code": 200
}

5191:[2026-04-30 20:57:59.555213] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"8224iqk8aqcsb0062d0c3f1ish"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
5291:[2026-04-30 20:57:59.575756] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"8224iqk8aqcsb0062d0c3f1ish"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
5480:[2026-04-30 20:57:59.623872] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"733jf4j6po8m6b1g7glgaghfsg"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
5624:[2026-04-30 20:57:59.663760] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"733jf4j6po8m6b1g7glgaghfsg"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
5655:[2026-04-30 20:57:59.788831] Admidio.INFO: Set Cookie! {"name":"ADMIDIO_admidio_adm_SESSION_ID","value":"ovnk3hhpj5829dj63pjk4i7k8b","expire":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":533,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"setCookie"}
5680:[2026-04-30 20:57:59.795443] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"ovnk3hhpj5829dj63pjk4i7k8b"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
5815:[2026-04-30 20:57:59.838697] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"ovnk3hhpj5829dj63pjk4i7k8b"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
5839:[2026-04-30 20:58:09.374182] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"dvrl2qf92skdeimh77ruglr4ga"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
5983:[2026-04-30 20:58:09.423217] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"dvrl2qf92skdeimh77ruglr4ga"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
6014:[2026-04-30 20:58:09.550875] Admidio.INFO: Set Cookie! {"name":"ADMIDIO_admidio_adm_SESSION_ID","value":"2th9qe9etfiis6nujdqpkfd9hv","expire":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":533,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"setCookie"}
6039:[2026-04-30 20:58:09.557823] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"2th9qe9etfiis6nujdqpkfd9hv"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
6273:[2026-04-30 20:58:19.171185] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"k50i1toh4491o6v0htliv2kafs"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
6417:[2026-04-30 20:58:19.212351] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"k50i1toh4491o6v0htliv2kafs"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
6448:[2026-04-30 20:58:19.337758] Admidio.INFO: Set Cookie! {"name":"ADMIDIO_admidio_adm_SESSION_ID","value":"4emiuth6i2fc1ho17nahf6n52g","expire":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":533,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"setCookie"}
6473:[2026-04-30 20:58:19.346804] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"4emiuth6i2fc1ho17nahf6n52g"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
6605:[2026-04-30 20:58:19.390909] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"4emiuth6i2fc1ho17nahf6n52g"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
6635:[2026-04-30 20:58:19.409216] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"4emiuth6i2fc1ho17nahf6n52g"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
6676:[2026-04-30 20:58:31.002317] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"aegildsksa0i5184igdk12pdg3"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
6820:[2026-04-30 20:58:31.045064] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"aegildsksa0i5184igdk12pdg3"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
6853:[2026-04-30 20:58:31.174884] Admidio.INFO: Set Cookie! {"name":"ADMIDIO_admidio_adm_SESSION_ID","value":"9vsc7c5qv9cr4cavugitg6i2l3","expire":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":533,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"setCookie"}
6878:[2026-04-30 20:58:31.184031] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"9vsc7c5qv9cr4cavugitg6i2l3"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
7010:[2026-04-30 20:58:40.393679] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"nr7mssfl6eupo9d2pboea7hmb2"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
7154:[2026-04-30 20:58:40.438503] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"nr7mssfl6eupo9d2pboea7hmb2"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
7185:[2026-04-30 20:58:40.564244] Admidio.INFO: Set Cookie! {"name":"ADMIDIO_admidio_adm_SESSION_ID","value":"sts5aqfsvqghtl6bfq79a3ap2t","expire":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":533,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"setCookie"}
7210:[2026-04-30 20:58:40.571305] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"sts5aqfsvqghtl6bfq79a3ap2t"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
7342:[2026-04-30 20:58:40.611506] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"sts5aqfsvqghtl6bfq79a3ap2t"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
7414:[2026-04-30 21:01:44.898211] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"dcgm8ebt3hkhmvvk9n860r6i5n"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
7558:[2026-04-30 21:01:44.940724] Admidio.INFO: Session Started! {"name":"ADMIDIO_admidio_adm_SESSION_ID","limit":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax","sessionId":"dcgm8ebt3hkhmvvk9n860r6i5n"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":617,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"start"}
7591:[2026-04-30 21:01:45.066694] Admidio.INFO: Set Cookie! {"name":"ADMIDIO_admidio_adm_AUTO_LOGIN_ID","value":"2:nO2BhCdRgFUMKT46e2EzS79Inf4oWiLWzLnX9Ko5","expire":1809118905,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":533,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"setCookie"}
7596:[2026-04-30 21:01:45.068352] Admidio.INFO: Set Cookie! {"name":"ADMIDIO_admidio_adm_SESSION_ID","value":"iga3ujr67cti6s7btnuhecte67","expire":0,"path":"/","domain":false,"secure":false,"httpOnly":true,"sameSite":"lax"} {"file":"/opt/app-root/src/src/Session/Entity/Session.php","line":533,"class":"Admidio\\Session\\Entity\\Session","callType":"::","function":"setCookie"}
```

## Impact

Any actor with log access can replay or abuse current session IDs and auto-login cookies, leading to session hijacking or long-lived account access depending on deployment and cookie lifetime.

## Remediation And Suggestions

Never log raw session identifiers or cookie values. Replace them with fixed labels or redact most of the value before logging.

```php
$gLogger->info('Set Cookie!', [
'name' => $name,
'value' => '[redacted]',
'expire' => $expire,
'path' => $path,
'domain' => $domain,
'secure' => $secure,
'httpOnly' => $httpOnly,
'sameSite' => 'lax',
]);

$gLogger->info('Session Started!', [
'name' => $sessionName,
'limit' => $limit,
'path' => $path,
'domain' => $domain,
'secure' => $secure,
'httpOnly' => $httpOnly,
'sameSite' => 'lax',
'sessionId' => '[redacted]',
]);
```

## References
- https://github.com/Admidio/admidio/security/advisories/GHSA-mch8-wf3h-6x88
- https://github.com/Admidio/admidio
