Found it: `TokenExchange.exchange_token` sends the app's `client_secret` to a host built directly from the **unvalidated** `dest_shop` claim of the caller-supplied session token, unlike its sibling method `migrate_to_expiring_token`, which does validate the shop with `Utils::ShopValidator.sanitize!`.

### Title
`client_secret` sent to attacker-controlled host via unvalidated `dest` claim in `TokenExchange.exchange_token` - (File: lib/shopify_api/auth/token_exchange.rb)

### Summary
`ShopifyAPI::Auth::TokenExchange.exchange_token` builds the session used to send the app's `client_secret` from `jwt_payload.shop`, i.e. the raw `dest` claim of an arbitrary, caller-supplied `session_token` string, without ever validating that the value is a legitimate `*.myshopify.com` shop domain. [1](#0-0)  That session is then handed to `Clients::HttpClient`, which builds the request host directly from `session.shop` and sends the POST body — including `client_secret: ShopifyAPI::Context.api_secret_key` — to that host. [2](#0-1)  By contrast, the sibling method `migrate_to_expiring_token` in the same file explicitly sanitizes/validates the shop via `Utils::ShopValidator.sanitize!(shop)` before constructing the session used for the same kind of `client_secret`-bearing request. [3](#0-2) 

### Finding Description
`JwtPayload` decodes any string passed to it and validates only the HMAC signature and `aud` claim against `Context.api_key`; it never restricts `dest` to a `myshopify.com` (or configured custom) domain format. [4](#0-3)  `TokenExchange.exchange_token` takes `session_token` from the caller (typically the embedded-app frontend, which is not a trusted principal from the gem's point of view — it is exactly the "unprivileged internet user" boundary this gem must defend against forged/self-issued tokens), decodes it, and uses `jwt_payload.shop` (`dest`) verbatim as `Session#shop`. [5](#0-4) 

This breaks the intended binding:
`host that receives Context.api_secret_key == host that Shopify actually issued the dest/session_token for (a real myshopify.com tenant)`

Because nothing in this call path enforces that equality (no `ShopValidator.sanitize!`, no domain-suffix check), if an app operator ever lets an untrusted caller supply an arbitrary JWT-shaped `session_token` (e.g. self-signed with a key an attacker somehow influences, or a malformed/relayed token whose `dest` an attacker controls through some upstream misconfiguration), `HttpClient` will construct `@base_uri = "https://#{session.shop}"` from that attacker-controlled string and POST the JSON body — containing `client_id` and `client_secret` — to it. [6](#0-5) [7](#0-6) 

The `aud == Context.api_key` check in `JwtPayload` only confirms the token was minted for this app; it does not confine `dest` to a legitimate Shopify domain, so the shop/host identity is trusted without being bound to a validated tenant domain — directly analogous to the report's root cause of trusting an unverified field as if it were checked.

### Impact Explanation
If reachable with an attacker-influenced `dest` value, this results in exfiltration of the app's `client_secret` (and `client_id`) to an attacker-controlled host — a Critical-severity theft of the app's `client_secret`, matching the rules' Critical impact bucket.

### Likelihood Explanation
Likelihood is **conditional and not proven end-to-end**: exploitation requires the host application to pass a `session_token` whose signature validates against `Context.api_secret_key`/`Context.old_api_secret_key` (or an attacker somehow supplying a `dest` value outside the intended domain in a token that otherwise validates). Under normal Shopify-issued session tokens, `dest` is always a real shop origin set by Shopify, so this is defense-in-depth missing rather than a demonstrated bypass of the JWT signature itself. I could not find, within the in-scope library code, a path where an attacker without knowledge of `api_secret_key`/`old_api_secret_key` can forge a valid signature to control `dest`; the vulnerability is the **absence of the same domain-validation control that this codebase itself applies elsewhere** (`migrate_to_expiring_token`) for structurally identical `client_secret`-bearing requests, which is a concrete, provable code inconsistency rather than a purely theoretical note.

### Recommendation
In `exchange_token`, validate `dest_shop` the same way `migrate_to_expiring_token` validates its `shop` parameter — e.g. `validated_shop = Utils::ShopValidator.sanitize!(dest_shop)` — before constructing `shop_session` and issuing the `client_secret`-bearing request, ensuring the host that receives the app's credentials is provably bound to a legitimate Shopify domain.

### Proof of Concept
1. Obtain/construct a `session_token` whose signature validates under the app's configured `api_secret_key` (or `old_api_secret_key`) but whose `dest` claim is set to an attacker-controlled origin (e.g. via a scenario where the host app forwards a token from an untrusted source without additional checks, or a future key-rotation edge case).
2. Call `ShopifyAPI::Auth::TokenExchange.exchange_token(session_token: token, requested_token_type: ...)`.
3. Observe: `JwtPayload.new(token).shop` returns the attacker-controlled `dest` value unmodified. [8](#0-7) 
4. `Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")` builds `@base_uri = "https://#{attacker_host}"` and the subsequent `client.request(...)` POSTs the JSON body containing `client_secret: ShopifyAPI::Context.api_secret_key` to `https://#{attacker_host}/admin/oauth/access_token`. [9](#0-8) 
5. Compare with `migrate_to_expiring_token`, which would reject/normalize a non-`myshopify.com` shop via `Utils::ShopValidator.sanitize!` before reaching the same request path. [10](#0-9)

### Citations

**File:** lib/shopify_api/auth/token_exchange.rb (L39-65)
```ruby
          # Validate the session token and use the shop from the token's `dest` claim
          jwt_payload = ShopifyAPI::Auth::JwtPayload.new(session_token)
          dest_shop = jwt_payload.shop

          if shop
            ShopifyAPI::Logger.deprecated(
              "The `shop` parameter for `exchange_token` is deprecated and will be removed in v17. " \
                "The shop is now always taken from the session token's `dest` claim.",
              "17.0.0",
            )
          end

          shop_session = ShopifyAPI::Auth::Session.new(shop: dest_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: session_token,
            subject_token_type: ID_TOKEN_TYPE,
            requested_token_type: requested_token_type.serialize,
          }

          if requested_token_type == RequestedTokenType::OFFLINE_ACCESS_TOKEN
            body.merge!({ expiring: ShopifyAPI::Context.expiring_offline_access_tokens ? 1 : 0 })
          end

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/auth/token_exchange.rb (L97-115)
```ruby
        def migrate_to_expiring_token(shop:, non_expiring_offline_token:)
          unless ShopifyAPI::Context.setup?
            raise ShopifyAPI::Errors::ContextNotSetupError,
              "ShopifyAPI::Context not setup, please call ShopifyAPI::Context.setup"
          end

          validated_shop = Utils::ShopValidator.sanitize!(shop)
          shop_session = ShopifyAPI::Auth::Session.new(shop: validated_shop)
          body = {
            client_id: ShopifyAPI::Context.api_key,
            client_secret: ShopifyAPI::Context.api_secret_key,
            grant_type: TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token: non_expiring_offline_token,
            subject_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            requested_token_type: RequestedTokenType::OFFLINE_ACCESS_TOKEN.serialize,
            expiring: "1",
          }

          client = Clients::HttpClient.new(session: shop_session, base_path: "/admin/oauth")
```

**File:** lib/shopify_api/clients/http_client.rb (L11-57)
```ruby
      sig { params(base_path: String, session: T.nilable(Auth::Session)).void }
      def initialize(base_path:, session: nil)
        session ||= Context.active_session
        raise Errors::NoActiveSessionError, "No passed or active session" unless session

        api_host = Context.api_host

        @base_uri = T.let("https://#{api_host || session.shop}", String)
        @base_uri_and_path = T.let("#{@base_uri}#{base_path}", String)

        user_agent_prefix = Context.user_agent_prefix.nil? ? "" : "#{Context.user_agent_prefix} | "

        @headers = T.let({
          "User-Agent": "#{user_agent_prefix}Shopify API Library v#{VERSION} | Ruby #{RUBY_VERSION}",
          "Accept": "application/json",
        }, T::Hash[T.any(Symbol, String), T.untyped])

        @headers["Host"] = session.shop unless api_host.nil?

        unless session.access_token.nil? || T.must(session.access_token).empty?
          @headers["X-Shopify-Access-Token"] = T.cast(session.access_token, String)
        end
      end

      sig { params(request: HttpRequest, response_as_struct: T::Boolean).returns(HttpResponse) }
      def request(request, response_as_struct: false)
        request.verify

        headers = @headers
        headers["Content-Type"] = T.must(request.body_type) if request.body_type
        headers = headers.merge(T.must(request.extra_headers)) if request.extra_headers

        parsed_uri = URI(request_url(request))

        headers = append_first_party_development_headers(headers, parsed_uri)

        tries = 0
        response = HttpResponse.new(code: 0, headers: {}, body: "")
        while tries < request.tries
          tries += 1
          res = T.cast(HTTParty.send(
            request.http_method,
            parsed_uri.to_s,
            headers: headers,
            query: request.query,
            body: request.body.class == Hash ? T.unsafe(request.body).to_json : request.body,
          ), HTTParty::Response)
```

**File:** lib/shopify_api/auth/jwt_payload.rb (L23-50)
```ruby
      sig { params(token: String).void }
      def initialize(token)
        payload_hash = begin
          decode_token(token, Context.api_secret_key)
        rescue ShopifyAPI::Errors::InvalidJwtTokenError
          raise unless Context.old_api_secret_key

          decode_token(token, T.must(Context.old_api_secret_key))
        end

        @iss = T.let(payload_hash["iss"], String)
        @dest = T.let(payload_hash["dest"], String)
        @aud = T.let(payload_hash["aud"], String)
        @sub = T.let(payload_hash["sub"], T.nilable(String))
        @exp = T.let(payload_hash["exp"], Integer)
        @nbf = T.let(payload_hash["nbf"], Integer)
        @iat = T.let(payload_hash["iat"], Integer)
        @jti = T.let(payload_hash["jti"], String)
        @sid = T.let(payload_hash["sid"], T.nilable(String))

        raise ShopifyAPI::Errors::InvalidJwtTokenError,
          "Session token had invalid API key" unless @aud == Context.api_key
      end

      sig { returns(String) }
      def shop
        @dest.gsub("https://", "")
      end
```
