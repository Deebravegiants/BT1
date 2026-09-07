# [H] Magento LTS's guest order "protect code" can be brute-forced too easily

## Summary
Severity: High
Advisory: GHSA-9358-cpvx-c2qp
CVE: CVE-2023-41879
CWE: CWE-330
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-09-11
Source: https://github.com/advisories/GHSA-9358-cpvx-c2qp
Type: github-advisory

## Affected
- Packagist: `openmage/magento-lts` — affected >=0 <19.5.1
- Packagist: `openmage/magento-lts` — affected >=20.0.0 <20.1.1

## Details
# Impact

Guest orders may be viewed without authentication using a "guest-view" cookie which contains the order's "protect_code". This code is 6 hexadecimal characters which is arguably not enough to prevent a brute-force attack. Exposing each order would require a separate brute force attack.

# Patches

None.

# Workarounds

Implementing rate-limiting at the web server would help mitigate the issue. In particular, a very strict rate limit (e.g. 1 per minute per IP) for the specific route (`sales/guest/view/`) would effectively mitigate the issue.

# References

Email from Frank Rochlitzer (f.rochlitzer@b3-it.de) to security@openmage.org:

## Summary

The German Federal Office for Information Security (BSI) found the following flaw in OpenMage through a commissioned pen test:
The web application was found to accept certain requests even without prior strong authentication if the person making the request has data that is non-public but also not secret, such as easily
easily guessed transaction numbers or names.
Attacking entities could possibly exploit this to retrieve sensitive information using this easier-to-obtain data and by trying random numbers.

## Details

Customers who place an order without an account can subsequently retrieve the order data or invoice data by specifying individual information.
Technically, the access is realized by specifying the cookie guest-view. The value of the cookie is Base64 encoded and contains a random value and the order number. The random value consists of six characters, where these are taken from the alphabet [0-9a-f]. In the best case, i.e. when using a cryptographically secure random number generator, this corresponds to an entropy of 24 bits. Furthermore, the order numbers are assigned incrementally, so that the number range can be narrowed down or an upper limit determined by placing an order.
Specifically, this results in the risk that an attacking entity can iterate over all possible values of the cookie's random value. If successful, the billing address, shipping address, payment details and the ordered items can be viewed. The attack only works for orders made as a guest.

## PoC

The request/response pair shows the retrieval of an order. It should be noted in particular, that the cookie is not bound to a session. The response has been formatted for formatted for readability.

Request:
```
1 GET /magento19/index.php/default/sales/guest/view/ HTTP/1.1
2 Host: localhost.local
3 Cookie: guest-view=MzYyYzI4OjEwMDAwMDQzMQ%3D%3D;
4 User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0
5 Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8
6 Accept-Language: en-US,en;q=0.5
7 Accept-Encoding: gzip, deflate
8 Referer: https://localhost.local/magento19/index.php/default/egovs_checkout/multipage/successview/
9 Upgrade-Insecure-Requests: 1
10 Sec-Fetch-Dest: document
11 Sec-Fetch-Mode: navigate
12 Sec-Fetch-Site: same-origin
13 Sec-Fetch-User: ?1
14 Te: trailers
15 Connection: close
```

Response:

```
1 HTTP/1.1 200 OK
2 Date: Tue, 13 Dec 2022 14:06:13 GMT
3 Server: Apache
4 Strict-Transport-Security: max-age=31536000; includeSubDomains
5 X-Powered-By: PHP/7.4.6
6 Set-Cookie: om_frontend=id7v84a05u8mm1j32t2kj5rbjl; expires=Tue, 13-Dec-2022 15:06:13 GMT; Max-Age=3600; path=/magento19/; domain=localhost.local; secure; HttpOnly
7 Expires: Thu, 19 Nov 1981 08:52:00 GMT
8 Cache-Control: no-store, no-cache, must-revalidate
9 Pragma: no-cache
10 Set-Cookie: om_frontend=deleted; expires=Thu, 01-Jan-1970 00:00:01 GMT; Max-Age=0; path=/magento19/; domain=localhost.local; secure; HttpOnly; SameSite=None
11 Set-Cookie: om_frontend=o42vttknheaj0sr3q0381jipdp; expires=Tue, 13-Dec-2022 15:06:13 GMT; Max-Age=3600; path=/magento19/; domain=localhost.local; secure; HttpOnly
12 Set-Cookie: guest-view=MzYyYzI4OjEwMDAwMDQzMQ%3D%3D; expires=Tue, 13-Dec-2022 14:16:13 GMT; Max-Age=600; path=/; domain=localhost.local; secure; HttpOnly; SameSite=None
13 X-Frame-Options: SAMEORIGIN
14 X-Content-Type-Options: nosniff
15 X-XSS-Protection: 1; mode=block
16 Referrer-Policy: same-origin
17 Feature-Policy: geolocation 'self'; vibrate 'none'
18 Content-Security-Policy: default-src 'self';script-src 'self' 'unsafe-inline' 'unsafeeval';
style-src 'self' 'unsafe-inline';
19 Connection: close
20 Content-Type: text/html; charset=UTF-8
21 Content-Length: 47876
22
23 <!DOCTYPE html>
24 <html xmlns="http://www.w3.org/1999/xhtml" xml:lang="de" lang="de">
25 […]
26 <div class="page-title">
27 <h1>Bestellung #100000431 - Ausstehende Überweisung</h1>
28 </div>
29 […]
30 <h2 class="feature-headline">Versandadresse</h2>
31 <div class="feature-content">
32 <address>
33 Herr Vorname Nachname<br>
34 Straße<br>
35 Dresden, Brandenburg, 01067<br>
36 Deutschland<br>
37 </address>
38 </div>
39 […]
40 <h2 class="feature-headline">Rechnungsadresse</h2>
41 <div class="feature-content">
42 <address>
43 [color]Herr Vorname Nachname<br>
44 Straße<br>
45 Dresden, Brandenburg, 01067<br>
46 Deutschland<br>[/color]
47 </address>
48 </div>
49 […]
50 <h2 class="feature-headline">Zahlungsart</h2>
51 <div class="feature-content">
52 <div class="block-content">
53 Vorkasse<br>
54 <div id="bankpayment_account_info" style="font-style: italic;">Bankverbindung</div>
55 <table class="data-table fieldset">
56 […]
57 <h2 class="sub-title">
58 <span>Kassenzeichen: WS1712000349</span>
59 </h2>
60 <h2 class="sub-title">Bestellte Artikel</h2>
61 […]
62 <td class="order-item-product">
63 <h3 class="product-name ellipsis-multi-line">Testprodukt Kreditkarte</h3>
64 […]
65 <span class="price">100,23 €</span>
66 […]
67 </html>
```

## Impact

Information disclosure.
Read as well as write access to sensitive information of persons or accounts and the execution of actions on their behalf must always be secured by strong authentication. This can be ensured, for example, by enforcing strong passwords or MFA.
For temporary accesses to sensitive information, temporary passwords or
authentication tokens or comparable data that an attacking entity cannot easily guess or determine should be used. Random values should have sufficient entropy so that searching the number space is impractical for attacking entities.
Furthermore, such queries should be limited by rate limiting.
The exact attack effort cannot be determined, since this requires the proportion of
the proportion of orders that were placed without an account and since the performance of the
performance of the production system is likely to differ from that of the test system.
In a test run, 1000 requests could be made within 36 seconds. Part of the execution is shown in the screenshot. The complete search of the number space for the random value would take 6 days 23 hours 46 minutes. Accordingly, the expected value is about 3.5 days. If every third order is executed without an account, the effort must be multiplied by a factor of 3.

Mit freundlichen Grüßen

Frank Rochlitzer (github: theroch)

## References
- https://github.com/OpenMage/magento-lts/security/advisories/GHSA-9358-cpvx-c2qp
- https://nvd.nist.gov/vuln/detail/CVE-2023-41879
- https://github.com/OpenMage/magento-lts/commit/2a2a2fb504247e8966f8ffc2e17d614be5d43128
- https://github.com/OpenMage/magento-lts/commit/31e74ac5d670b10001f88f038046b62367f15877
- https://github.com/OpenMage/magento-lts
- https://github.com/OpenMage/magento-lts/releases/tag/v19.5.1
- https://github.com/OpenMage/magento-lts/releases/tag/v20.1.1
