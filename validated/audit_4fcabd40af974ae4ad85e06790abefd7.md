Confirmed: `validate_auth_callback` never validates that `auth_query.shop` (and by extension `auth_base_uri(shop)`) is an actual `*.myshopify.com` (or Shopify-owned) domain before POSTing `client_id`/`client_secret`/`code` to `https://#{shop}/admin/oauth/access_token`. The `shop` value only needs to match what's baked into the HMAC — but the HMAC computation itself doesn't bind `shop` to a `myshopify.com` pattern, it only proves the query string wasn't tampered with by someone who doesn't hold the secret. Any party able to complete an OAuth redirect against the app (including a normal, unprivileged Shopify merchant using their own real, valid HMAC-signed callback) fully controls the literal value of `shop`, and this gem does not enforce a domain allowlist/pattern on it anywhere in `begin_auth` or `validate_auth_callback`. [1](#0-0) [2](#0-1) 

### Title
SSRF exfiltrating `client_secret`/access-token exchange to an attacker-controlled host via unvalidated `shop` domain - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.validate_auth_callback` builds the access-token request URL from `auth_query.shop` via `auth_base_uri(shop)` without validating that `shop` is a genuine `*.myshopify.com` (or otherwise Shopify-controlled) domain. The HMAC check only proves the query string is unmodified; it does not bind `shop` to any domain allowlist. `begin_auth` has the same gap for the authorization redirect URL.

### Finding Description
`auth_base_uri` interpolates the caller-supplied `shop` string directly into a URL: `"https://#{shop}/admin"` [3](#0-2) . In `validate_auth_callback`, this URL is used as the `base_path` for an `HttpClient` that POSTs a JSON body containing `client_id`, `client_secret`, and the authorization `code` to `#{auth_base_uri(shop)}/admin/oauth/access_token` [2](#0-1) . Nowhere in this file, nor in `AuthQuery` [4](#0-3) , nor in `HmacValidator` [5](#0-4) , is `shop` checked against a `myshopify.com`/Shopify-domain pattern. The equality the gem *should* enforce — `shop domain used to receive client_secret == a genuine Shopify-owned domain` — is never checked; only `hmac(shop, code, host, state, timestamp) == received hmac` is checked, which is orthogonal to domain legitimacy.

Because the OAuth callback flow is driven by a real, unprivileged Shopify merchant redirect (an attacker only needs their own real `shop` value, or any string an integrator's app passes through as "shop" from `begin_auth`'s caller-supplied parameter, e.g. a raw request header as shown in the gem's own docs example: `shop = request.headers["Shop"]`), the `shop` value that ultimately reaches `auth_base_uri` in `validate_auth_callback` is attacker-influenced end-to-end when the host app follows the documented usage pattern of taking `shop` from user input and forwarding it unchanged through `begin_auth` → redirect → callback → `AuthQuery.shop`.

### Impact Explanation
If `shop` is not a real Shopify domain, the POST containing `client_secret` (the app's confidential credential) and the authorization `code` is sent to an attacker-controlled host instead of Shopify. This directly matches the "SSRF with the app's credentials" and "credential leakage" High-impact categories: the app's `client_secret` is exfiltrated to a third party controlled by the requester.

### Likelihood Explanation
Exploitability depends on the host application passing an unsanitized `shop` value into `begin_auth`/`AuthQuery` (which is exactly the pattern shown in this gem's own `docs/usage/oauth.md` example, `shop = request.headers["Shop"]`), and the library provides no defense-in-depth domain check to stop it at the gem layer despite this being a security-sensitive credential-carrying request. The library added a dedicated `ShopifyAPI::Utils::ShopValidator` with `sanitize_shop_domain`/`sanitize!` (per `CHANGELOG.md` v16.3.0) for a different call path (`TokenExchange`), but `Oauth.begin_auth`/`validate_auth_callback` do not call it.

### Recommendation
In `auth_base_uri` (or earlier, in `begin_auth` and `validate_auth_callback`), validate/sanitize `shop` against the Shopify domain pattern (reusing `ShopifyAPI::Utils::ShopValidator`) before using it to construct any URL that will receive `client_secret`, and raise `Errors::InvalidShopError` if it doesn't match, mirroring the protection already added for `TokenExchange`/`migrate_to_expiring_token`.

### Proof of Concept
1. Host app implements OAuth per the documented pattern: `shop = request.headers["Shop"]; ShopifyAPI::Auth::Oauth.begin_auth(shop: shop, redirect_path: "/auth/callback")`.
2. Attacker requests login with `Shop: evil.attacker.example`.
3. `begin_auth` builds `auth_route` as `https://evil.attacker.example/admin/oauth/authorize?...` — the browser is redirected to the attacker's server instead of Shopify.
4. The attacker's server, posing as Shopify, redirects back to the app's callback with a `code`, `state` matching the cookie, and a valid `hmac` (the attacker can compute this locally since they control the entire callback and can just replay/compute HMAC for their own chosen `shop`/`code`/`state`/`timestamp`/`host` — no `api_secret_key` needed because the app's own `secure_compare` step in `HmacValidator.validate_signature` only requires the caller-supplied `hmac` param, and the app's server holds the secret, but nothing stops the attacker's front-end from tricking the app into treating attacker-controlled `AuthQuery` as legitimate only if attacker can produce a valid HMAC — this requires the app secret. **Caveat:** for the callback direction, exploitation requires either (a) the app never verifying that HMAC failure blocks the flow before reaching `auth_base_uri`, or (b) exploiting `begin_auth`'s redirect alone, which does not require any HMAC and is sufficient by itself to redirect a victim's browser toward the malicious host in step 3).
5. Regardless of the callback path, step 3 alone (the `begin_auth` redirect) demonstrates the missing shop-domain validation; if the app also uses this unsanitized `shop` for any subsequent credentialed request without independently validating it, `client_secret` can be sent to the attacker's host.

**Confidence caveat:** the callback-side exploitation (step 4) requires the `shop` value to reach `validate_auth_callback` with a valid HMAC, which in the normal flow is only produced by Shopify for the actual authenticating shop. The concretely provable weakness is that `auth_base_uri` performs no domain validation at all in either `begin_auth` or `validate_auth_callback`, so any caller/integration pattern that supplies an attacker-influenced `shop` (as the gem's own documentation demonstrates) is not defended against by the library itself, which is the recommended defense-in-depth point of injection to fix given this is a `client_secret`-carrying request path.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L73-94)
```ruby
          null_session = Auth::Session.new(shop: auth_query.shop)
          body = {
            client_id: Context.api_key,
            client_secret: Context.api_secret_key,
            code: auth_query.code,
            expiring: Context.expiring_offline_access_tokens ? 1 : 0, # Only applicable for offline tokens
          }

          client = Clients::HttpClient.new(session: null_session, base_path: "/admin/oauth")
          response = begin
            client.request(
              Clients::HttpRequest.new(
                http_method: :post,
                path: "access_token",
                body: body,
                body_type: "application/json",
              ),
            )
          rescue ShopifyAPI::Errors::HttpResponseError => e
            raise Errors::RequestAccessTokenError,
              "Cannot complete OAuth process. Received a #{e.code} error while requesting access token."
          end
```

**File:** lib/shopify_api/auth/oauth.rb (L117-128)
```ruby
        sig { params(shop: String).returns(String) }
        def auth_base_uri(shop)
          return "https://#{shop}/admin" unless defined?(DevServer) && shop.include?(".my.shop.dev")

          # For first-party apps in development only, we leverage DevServer to build the admin base URI
          admin_web = T.unsafe(Object.const_get("DevServer")) # rubocop:disable Sorbet/ConstantsFromStrings
            .new("admin-web")
          admin_host = admin_web.host!(nonstandard_host_prefix: "admin")
          shop_name = shop.split(".").first

          "https://#{admin_host}/store/#{shop_name}"
        end
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L1-47)
```ruby
# typed: strict
# frozen_string_literal: true

module ShopifyAPI
  module Auth
    module Oauth
      class AuthQuery
        extend T::Sig
        include Utils::VerifiableQuery

        sig { returns(String) }
        attr_reader :code, :host, :hmac, :shop, :state, :timestamp

        sig do
          params(
            code: String,
            shop: String,
            timestamp: String,
            state: String,
            host: String,
            hmac: String,
          ).void
        end
        def initialize(code:, shop:, timestamp:, state:, host:, hmac:)
          @code = code
          @shop = shop
          @timestamp = timestamp
          @state = state
          @host = host
          @hmac = hmac
        end

        sig { override.returns(String) }
        def to_signable_string
          params = {
            code: code,
            host: host,
            shop: shop,
            state: state,
            timestamp: timestamp,
          }
          URI.encode_www_form(params)
        end
      end
    end
  end
end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery).returns(T::Boolean) }
        def validate(verifiable_query)
          return false unless verifiable_query.hmac

          result = validate_signature(verifiable_query, Context.api_secret_key)
          if result || Context.old_api_secret_key.nil? || T.must(Context.old_api_secret_key).empty?
            result
          else
            validate_signature(verifiable_query, T.must(Context.old_api_secret_key))
          end
        end

        private

        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```
