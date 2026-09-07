# [H] Astro vulnerable to reflected XSS via the server islands feature

## Summary
Severity: High
Advisory: GHSA-wrwg-2hg8-v723
CVE: CVE-2025-64764
CWE: CWE-79, CWE-80
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:H/A:N (CVSS_V3)
Published: 2025-11-19
Source: https://github.com/advisories/GHSA-wrwg-2hg8-v723
Type: github-advisory

## Affected
- npm: `astro` — affected >=0 <5.15.8

## Details
## Summary
After some research it appears that it is possible to obtain a reflected XSS when the server islands feature is used in the targeted application, **regardless of what was intended by the component template(s)**.

## Details
Server islands run in their own isolated context outside of the page request and use the following pattern path to hydrate the page: `/_server-islands/[name]`. These paths can be called via GET or POST and use three parameters:

- `e`: component to export
- `p`: the transmitted properties, encrypted
- `s`: for the slots

Slots are placeholders for external HTML content, and therefore allow, by default, the injection of code if the component template supports it, nothing exceptional in principle, just a feature.

This is where it becomes problematic: it is possible, independently of the component template used, even if it is completely empty, to inject a slot containing an XSS payload, whose parent is a tag whose name is is the absolute path of the island file. Enabling reflected XSS on any application, regardless of the component templates used, provided that the server islands is used at least once.

**How ?**

By default, when a call is made to the endpoint `/_server-islands/[name]`, the value of the parameter `e` is `default`, pointing to a function exported by the component's module.

Upon further investigation, we find that two other values ​​are possible for the component export (param `e`) in a typical configuration: `url` and `file`. `file` returns a string value corresponding to the absolute path of the island file. Since the value is of type `string`, it fulfills the following condition and leads to [this code block](https://github.com/withastro/astro/blob/190106149908ef6826899459146ef9f0ead602ab/packages/astro/src/runtime/server/render/component.ts#L279):

<img width="804" height="571" alt="image" src="https://github.com/user-attachments/assets/25ea6c16-fc27-477a-a1ad-e5edf0819b31" />

An entire template is created, completely independently, and then returned:

- the absolute path name is sanitized and then injected as the tag name
- `childSlots`, the value provided to the `s` parameter, is injected as a child

All of this is done using `markHTMLString`. This allows the injection of any XSS payload, **even if the component template intended by the application is initially empty or does not provide for the use of slots.**

## Proof of concept
For our Proof of Concept (PoC), we will use a minimal repository:
- Latest Astro version at the time (5.15.6)
- Use of Island servers, with a completely empty component, to demonstrate what we explained previously

[Download the PoC repository](https://github.com/zhero-web-sec/astro-app-2)

Access the following URL and note the opening of the popup, demonstrating the reflected XSS:

http://localhost:4321/_server-islands/ServerTime?e=file&p=&s={%22zhero%22:%22%3Cimg%20src=x%20onerror=alert(0)%3E%22}

<img width="1781" height="529" alt="image" src="https://github.com/user-attachments/assets/92f8134a-d1c7-4d3f-818e-214842c239c8" />

The value of the parameter `s` must be in JSON format and the payload must be injected at the value level, not the key level : 

<img width="3273" height="1840" alt="for_respected_patron" src="https://github.com/user-attachments/assets/8ac0079a-3dee-49e8-b639-322f77c84b83" />

Despite the initial template being empty, it is created because the value of the URL parameter `e` is set to `file`, as explained earlier. The parent tag is the name of the component's internal route, and its child is the value of the key "zhero" (*the name doesn't matter*) of the URL parameter `s`.

## Credits
- Allam Rachid ([zhero;](https://zhero-web-sec.github.io/research-and-things/))
- Allam Yasser (inzo)

## References
- https://github.com/withastro/astro/security/advisories/GHSA-wrwg-2hg8-v723
- https://nvd.nist.gov/vuln/detail/CVE-2025-64764
- https://github.com/withastro/astro/commit/790d9425f39bbbb462f1c27615781cd965009f91
- https://github.com/withastro/astro
