# [M] Django REST framework: AdminRenderer may disclose GET-protected data when rendering invalid write requests

## Summary
Severity: Medium
Advisory: GHSA-g47c-3xmw-q6m2
CVE: CVE-2026-73229
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2026-09-01
Source: https://github.com/advisories/GHSA-g47c-3xmw-q6m2
Type: github-advisory

## Affected
- PyPI: `djangorestframework` — affected >=0 <3.17.2

## Details
Summary

AdminRenderer may disclose data that would normally be protected by GET permissions when rendering a 400 Bad Request response for an invalid write request.

If a view allows POST (or another write method) but denies GET, an invalid request rendered through AdminRenderer can invoke the view's GET handler and include data from the GET representation in the generated HTML response.

This behavior appears to be specific to AdminRenderer and does not affect the normal JSON rendering path.


---

Details

While investigating the AdminRenderer rendering flow, I observed that invalid write requests are rendered by temporarily overriding the request method and invoking the view's GET handler:

```
with override_method(view, request, "GET") as request:
    response = view.get(request, *view.args, **view.kwargs)

data = response.data
```

This execution path differs from a normal GET request.

Under normal request processing, a GET request flows through:

```
APIView.dispatch()
    └── APIView.initial()
            └── APIView.check_permissions()
```

However, during AdminRenderer rendering, the renderer directly invokes:

view.get(...)

A view whose permission class explicitly allowed POST but denied GET still executed its GET handler while rendering an invalid POST request through AdminRenderer.

As a result, data intended to be available only through an authorized GET request was included in the generated HTML response.


---

Proof of Concept

Using a standard ListCreateAPIView.

Permission class:

```
class ProbePermission(BasePermission):
    def has_permission(self, request, view):
        return request.method == "POST"

View:

class View(ListCreateAPIView):
    renderer_classes = (AdminRenderer, JSONRenderer)
    permission_classes = (ProbePermission,)
    serializer_class = ProbeSerializer

    def get_queryset(self):
        return [
            {
                "name": "visible",
                "secret": "GET-ONLY-SECRET",
            }
        ]
```

Expected Behaviour

```
GET request
→ 403 Forbidden

Invalid POST request
→ 400 Bad Request
→ Response should contain only validation errors.
→ GET-only data should not be rendered.

```
Observed Behaviour

```
GET request
→ 403 Forbidden

Invalid POST request rendered through AdminRenderer
→ 400 Bad Request
→ HTML response contains:

GET-ONLY-SECRET
```

Tthe same behavior is shown using a minimal APIView implementation.

Observed results:

```
minimal.post_400.handler_calls =
[
    ("post", "POST"),
    ("get", "GET")
]

minimal.post_400.contains_secret = True
```

Generic view reproduction:

```
generic.direct_get.status = 403
generic.direct_get.contains_secret = False

generic.post_400.status = 400
generic.post_400.contains_secret = True

generic.post_400.permission_calls =
[
    ("GenericAdminView", "POST"),
    ...
    ("GenericAdminView", "OPTIONS")
]

generic.post_400.queryset_calls =
[
    ("GenericAdminView", "GET"),
    ...
]
```

These observations indicate that direct GET requests are correctly denied, while the simulated GET used during AdminRenderer rendering can still retrieve the protected representation.


---

Impact

This issue may result in information disclosure when all of the following conditions are met:

AdminRenderer is enabled.

The client negotiates the HTML renderer (for example using Accept: text/html).

The application permits POST (or another write method).

GET requests are denied by the configured permission class.

The invalid write request returns 400 Bad Request.

The GET representation contains information that the requester would normally not be permitted to access.


This issue does not appear to affect:

JSON rendering

Standard API responses

Successful write requests


The behavior appears limited to the HTML rendering path used by AdminRenderer.


---

Suggested Fix

Possible approaches include:

Perform equivalent permission checks before executing the simulated GET request.

Avoid invoking view.get() when the corresponding GET request would not be permitted.

Fall back to rendering only serializer/form validation errors instead of retrieving the GET representation.


A regression test could create a permission class that allows POST while denying GET, then verify that an invalid POST rendered with AdminRenderer does not include data from the protected GET representation.


---

Environment

Repository:

`encode/django-rest-framework`

Branch tested:

`security-audit-drf`

Commit tested:

`cf582fb58e9e5ffcc8ed78a2cb9aaa8f4865666a`

## References
- https://github.com/encode/django-rest-framework/security/advisories/GHSA-g47c-3xmw-q6m2
- https://nvd.nist.gov/vuln/detail/CVE-2026-73229
- https://github.com/encode/django-rest-framework/pull/10012
- https://github.com/encode/django-rest-framework/commit/71f81946906e52f9dc8e5d22a0f3d2afa50c455e
- https://github.com/encode/django-rest-framework/commit/9e82afc98acfe6fc28c9bf78147f0c5b3f222cb5
- https://github.com/encode/django-rest-framework
- https://github.com/encode/django-rest-framework/releases/tag/3.17.2
