# [M] Reflected Cross Site-Scripting (XSS) in Oveleon Cookiebar

## Summary
Severity: Medium
Advisory: GHSA-296q-rj83-g9rq
CVE: CVE-2024-47069
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-07-26
Source: https://github.com/advisories/GHSA-296q-rj83-g9rq
Type: github-advisory

## Affected
- Packagist: `oveleon/contao-cookiebar` — affected >=0 <1.16.3
- Packagist: `oveleon/contao-cookiebar` — affected >=2.0.0 <2.1.3

## Details
## usd-2024-0009 | Reflected XSS in Oveleon Cookiebar

### Details
**Advisory ID**: usd-2024-0009 
**Product**: Cookiebar   
**Affected Version**: 2.X  
**Vulnerability Type**: CWE-79: Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting')   
**Security Risk**: HIGH, CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:A/VC:N/VI:L/VA:N/SC:L/SI:L/SA:N   
**Vendor URL**: https://www.usd.de/    
**Vendor acknowledged vulnerability**: Yes    
**Vendor Status**: Fixed   
**CVE Number**: Not requested yet    
**CVE Link**: Not requested yet    
**First Published**: Published  
**Last Update**: 2024-07-29


### Affected Component

The `block` function in `CookiebarController.php`.


### Desciption

Oveleon's Cookiebar is an extension for the popular Contao CMS.
The `block/locale` endpoint does not properly sanitize the user-controlled `locale` input before including it in the backend's HTTP response, thereby causing reflected XSS.

### Proof of Concept
The vulnerability could be triggered by entering the following Link:

```
https://[redacted].de/cookiebar/block/dens82w%22%3E%3Cimg%20src%3da%20onerror%3dalert(1)%3Ew9qt
n/[id]?redirect=https%3A%2F%2F[...]amp%3Biv_load_policy%3D3%26amp%3Bmo
destbranding%3D1%26amp%3Brel%3D0
```

It is likely related to the following function in the Oveleon Cookiebar source code:

```php
    /**
     * Block content
     *
     * @Route("/cookiebar/block/{locale}/{id}", name="cookiebar_block")
     */
    public function block(Request $request, string $locale, int $id): Response
    {
        System::loadLanguageFile('tl_cookiebar', $locale);

        $this->framework->initialize();

        $objCookie = CookieModel::findById($id);

        if (null === $objCookie || null === $request->headers->get('referer'))
        {
            throw new PageNotFoundException();
        }

        $strUrl = $request->get('redirect');

        // Protect against XSS attacks
        if(!Validator::isUrl($strUrl))
        {
            return new Response('The redirect destination must be a valid URL.', Response::HTTP_BAD_REQUEST);
        }

        $objTemplate = new FrontendTemplate($objCookie->blockTemplate ?: 'ccb_element_blocker');

        $objTemplate->language = $locale;
        $objTemplate->id = $objCookie->id;
        $objTemplate->title = $objCookie->title;
        $objTemplate->type = $objCookie->type;
        $objTemplate->iframeType = $objCookie->iframeType;
        $objTemplate->description = $objCookie->blockDescription;
        $objTemplate->redirect = $request->get('redirect');
        $objTemplate->acceptAndDisplayLabel = $this->translator->trans('tl_cookiebar.acceptAndDisplayLabel', [], 'contao_default', $locale);

        return $objTemplate->getResponse();
    }
```

### Fix
Sanitize the `locale` input to prevent XSS payloads from being executed in a user's browser.


### References
- https://github.com/oveleon/contao-cookiebar/blob/2.x/src/Controller/CookiebarController.php
- https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html


### Timeline
* **2024-04-24**: Vulnerability discovered by DR of usd AG.
* **2024-07-25**: Probable cause of the vulnerability has been identified as Oveleon's Cookiebar Extension for Contao CMS.
* **2024-07-25**: Vulnerability disclosed via GitHub Vulnerability Report.


### Credits
This security vulnerability was identified by DR of usd AG.


### About usd Security Advisories
In order to protect businesses against hackers and criminals, we always have to keep our skills and knowledge up to date. Thus, security research is just as important for our work as is building up a security community to promote the exchange of knowledge. After all, more security can only be achieved if many individuals take on the task.

Our CST Academy and our usd HeroLab are essential parts of our security mission. We share the knowledge we gain in our practical work and our research through training courses and publications. In this context, the usd HeroLab publishes a series of papers on new vulnerabilities and current security issues. 

Always for the sake of our mission: "more security."

https://www.usd.de


### Disclaimer
The information provided in this security advisory is provided "as is" and without warranty of any kind. Details of this security advisory may be updated in order to provide as accurate information as possible.

## References
- https://github.com/oveleon/contao-cookiebar/security/advisories/GHSA-296q-rj83-g9rq
- https://nvd.nist.gov/vuln/detail/CVE-2024-47069
- https://github.com/oveleon/contao-cookiebar/commit/1d57470be5878f66d5e1e23f624dd387564b9b8d
- https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html
- https://github.com/oveleon/contao-cookiebar
- https://github.com/oveleon/contao-cookiebar/blob/2.x/src/Controller/CookiebarController.php
