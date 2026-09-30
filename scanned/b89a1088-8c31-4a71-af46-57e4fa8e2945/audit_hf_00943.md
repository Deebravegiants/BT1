# [M] Content Spoofing via Parameters

## Summary
Severity: Medium
Contest weight: 0.3905
Dataset id: 2906
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Content spoofing, also known as content injection, arbitrary text injection, or virtual defacement, is an attack targeting a user through a vulnerability in a web application. This occurs when the application improperly handles user-supplied data, allowing an attacker to inject content, typically via a parameter value, which is then reflected back to the user. This results in the user seeing a modified page under the trusted domain's context. Often, this type of attack is combined with social engineering tactics, exploiting both a code-based vulnerability and the user's trust.
The impact of a content spoofing attack varies based on context. If user-supplied information is reflected in a way that is correctly escaped and clearly visually marked, such as in error messages, it may be harmless. However, if the input is not clearly visually distinguished from the legitimate content, it can be used in social engineering attacks. Moreover, if the input is not correctly escaped, it may contain active components, enabling attacks similar to Cross-site Scripting (XSS).
In the specific case of allyourbase.virtual.tech, parameters url, w and q can be modified to reflect the frontend changes/defacements directly in the response. The parameters can be used initially to self-deface the website as the application allows the user to change the values on the fly while the components are loading.

## Proof of Concept
Using a proxy intercept the request when browsing to allyourbase.virtual.tech. The following GET request will be available:
GET /_next/image?url=%2Ficons%2Fclassic.png&w=48&q=75 HTTP/2
Host: allyourbase.virtual.tech
// Other headers not shown.
From the request above, you can see that parameter url, w and q are having predictable values that can be modified in the request and overalls are parsed by the frontend. Similarly as the content spoofing vulnerability from above we are able to modify the parameter with different values and the following error messages appear:
Request:
GET /_next/image?url=%2F../../../&w=828&q=011-10 HTTP/2
Host: allyourbase.virtual.tech
Response:
HTTP/2 400 Bad Request
Unable to optimize image and unable to fallback to upstream image
Request:
GET /_next/image?url=%2Ffoo.png&w=828&q=011-10 HTTP/2
Host: allyourbase.virtual.tech
Response:
HTTP/2 400 Bad Request
The requested resource isn't a valid image.
For parameters q and w:
Request:
GET /_next/image?url=%2Ficons%2Fclassic.png&w=48&q=7500 HTTP/2
Host: allyourbase.virtual.tech
Response:
”q” parameter (quality) must be a number between 1 and 100
Request:
GET /_next/image?url=%2Ficons%2Fclassic.png&w=4800&q=75 HTTP/2
Host: allyourbase.virtual.tech
Response:
”w” parameter (width) of 4800 is not allowed
It is clear that application response changes according to the url, q and w values which are allowed to be modified on the fly. In this way, when content is loading, it is possible to execute a defacement by changing the values of the images loading: We modify the tails image for heads on the fly (which will be processed by the application) in this example:

Figure 1: Response (rendered):
Figure 2: Original

## Recommendation
Filter all supplied content to the parameters ‘url‘, ‘w‘, and ‘q‘, especially since these are programmatically defined. Although this may seem like self-defacement, users should not be able to modify the contents of a defined web application, even within their own session.
