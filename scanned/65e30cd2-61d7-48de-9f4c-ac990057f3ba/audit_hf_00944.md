# [M] Improper Error Handling in Parameters

## Summary
Severity: Medium
Contest weight: 0.3659
Dataset id: 2908
Source: https://huggingface.co/datasets/Zaevlad/audit-findings-dataset
Type: audit-finding

## Details
Improper error handling can introduce numerous security issues for a website. The most common issue arises when detailed internal error messages, such as stack traces, database dumps, and error codes, are displayed to users (potential attackers). These messages reveal implementation details and vulnerabilities in the site. Additionally, such messages can be disturbing for regular users.
Web applications often generate error conditions during normal operation, such as out-of-memory errors, null pointer exceptions, system call failures, database unavailability, and network timeouts. These errors must be managed according to a well-designed scheme that provides meaningful error messages to users, diagnostic information to site maintainers, and no useful information to attackers.
Even when error messages lack detail, inconsistencies in these messages can still reveal critical information about a site's inner workings and the data it contains. For example, an error message stating ”file not found” when a user attempts to access a non-existent file, and ”access denied” when trying to access a restricted file, can inadvertently disclose the existence of hidden files or the site's directory structure. This inconsistency allows users to infer the presence or absence of files they should not be aware of.
In the specific case of allyourbase.virtual.tech, the application does not gracefully handle the errors displayed when the user supplies values for the given parameters, as described in the PoC below.

## Proof of Concept
Using a proxy intercept the request when browsing to allyourbase.virtual.tech. The following GET request will be available: GET /_next/image?url=%2Ficons%2Fclassic.png&w=48&q=75 HTTP/2
Host: allyourbase.virtual.tech // Other headers not shown. From the request above, you can see that parameter url, w and q are having predictable values that can be modified in the request and overalls are parsed by the frontend. Similarly as the content spoofing vulnerability from above we are able to modify the parameter with different values and the following error messages appear: Request: GET /_next/image?url=%2F../../../&w=828&q=011-10 HTTP/2 Host: allyourbase.virtual.tech Response: HTTP/2 400 Bad Request Unable to optimize image and unable to fallback to upstream image Request: GET /_next/image?url=%2Ffoo.png&w=828&q=011-10 HTTP/2 Host: allyourbase.virtual.tech Response: HTTP/2 400 Bad Request The requested resource isn’t a valid image. For parameters q and w: Request: GET /_next/image?url=%2Ficons%2Fclassic.png&w=48&q=7500 HTTP/2 Host: allyourbase.virtual.tech Response: “q” parameter (quality) must be a number between 1 and 100 Request: GET /_next/image?url=%2Ficons%2Fclassic.png&w=4800&q=75 HTTP/2 Host: allyourbase.virtual.tech Response: ”w” parameter (width) of 4800 is not allowed

## Recommendation
Effective error handling mechanisms must manage any feasible set of inputs while ensuring robust security measures. They should generate clear and concise error messages, which are then logged to facilitate the review of their causes, whether stemming from site errors or potential hacking attempts. Furthermore, error handling should not be limited to user inputs; it must also encompass errors arising from internal components, including system calls, database queries, and other internal functions.
