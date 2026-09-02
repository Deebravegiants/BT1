### Title
Webhook `shop-domain` (and `topic`) headers are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw request body, never the `shop-domain` or `topic` headers. `ShopifyAPI::Webhooks::Registry.process` verifies the HMAC over that signable string and, once it passes, unconditionally trusts `request.shop` and `request.topic` (parsed straight from unsigned headers) to build the `WebhookMetadata` handed to the app's handler. Because the shop identity is never bound to the cryptographic signature, a genuine `(body, hmac)` pair obtained from one tenant can be replayed with a different `shop-domain` header to make the app process the payload as if it came from a completely different shop.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

which returns only `@raw_body`. The `shop` and `topic` accessors are read from HTTP headers that are never mixed into that signable string: [2](#0-1) 

`Utils::HmacValidator.validate` computes `HMAC(secret, to_signable_string)` and compares it to the `hmac-sha256` header — it never sees the `shop-domain` header at all: [3](#0-2) 

`Registry.process` treats a passing HMAC check as proof of everything in the request, including `request.shop`, and forwards it straight to the app-supplied handler as the tenant identifier: [4](#0-3) 

The `api_secret_key` used to sign webhooks is a single secret shared by the app across **every** installing shop (the same secret used for OAuth HMACs and session-token JWTs, see `Context.api_secret_key` usage in `HmacValidator` and `JwtPayload`). That means any unprivileged user who installs the app on their own store legitimately receives `(raw_body, hmac)` pairs correctly signed with that shared secret for their own shop's events. Because the `shop-domain` header sits outside the signed bytes, that same attacker can resend the identical body+HMAC to the app's public webhook endpoint while substituting an arbitrary `x-shopify-shop-domain` value (e.g. a victim shop's domain). `HmacValidator.validate` still succeeds — it only checks the body — and `Registry.process` passes the forged shop straight through to `WebhookMetadata`/the handler, which is exactly the value host apps are expected to use for tenant routing.

This is the same class of bug as the reported issue: a value that is acted upon (the `shop-domain` used for tenant identification) is not covered by the security check (`whenNotPaused` there; the HMAC signature here) that is supposed to gate the operation.

Contrast this with `Auth::Oauth::AuthQuery`, where `shop` *is* included in `to_signable_string` and thus is cryptographically bound to the HMAC: [5](#0-4) 

and with `Auth::JwtPayload`, where the shop (`dest` claim) lives *inside* the signed JWT payload rather than in a separate unsigned header: [6](#0-5) 

The webhook path is the outlier: it authenticates bytes (`raw_body`) that are disjoint from the identity field (`shop`) that is actually consumed for tenant attribution.

### Impact Explanation
This breaks the identity binding `authenticated(shop) == acted_on(shop)`. An attacker who is nothing more than an installer of the target app (an unprivileged internet user, no access token or leaked credentials required) can forge webhook deliveries that are attributed to any other shop of their choosing, because the HMAC only proves the body was signed by the app's secret — not which shop the body belongs to. Depending on how the host application's webhook handler uses `WebhookMetadata#shop` (e.g., to look up/create/update per-tenant records, trigger per-tenant side effects, or write into a per-shop database row), this enables cross-tenant data injection/corruption attributed to a shop the attacker does not own.

### Likelihood Explanation
Any user can install a publicly-available app that uses this gem on their own store, which is enough to obtain valid `(raw_body, hmac)` pairs signed with the app's shared `api_secret_key`. From there, forging the `shop-domain` header on a replayed request to the app's public webhook endpoint requires no special access, tooling, or secret — only knowledge of the endpoint URL, which is typically discoverable/predictable for a given app.

### Recommendation
Bind the shop (and topic) into the signed material, or otherwise cryptographically verify them, before trusting `request.shop`/`request.topic`:
- Include `shop-domain` (and `topic`, `webhook-id`) in `Request#to_signable_string` (mirroring `AuthQuery#to_signable_string`), and require callers/host apps to independently confirm the shop domain is one that is actually installed/known before acting on the payload, rather than trusting the header alone.
- At minimum, document clearly that `Registry.process`'s HMAC check does not authenticate the `shop-domain` header, so host applications must not use it as a sole tenant-identification value for privileged/write operations without an additional binding (e.g., cross-checking against a known installed-shop list).

### Proof of Concept
1. Attacker signs up for the target Shopify app on their own store `attacker.myshopify.com` and registers/receives a webhook (e.g. `orders/create`). Shopify sends: `raw_body = B`, headers include `x-shopify-hmac-sha256: H` (valid HMAC of `B` with the app's shared `api_secret_key`) and `x-shopify-shop-domain: attacker.myshopify.com`.
2. Attacker replays the exact same request to the app's public webhook endpoint, but overwrites the header: `x-shopify-shop-domain: victim.myshopify.com`. `x-shopify-hmac-sha256` stays `H`, body stays `B`.
3. Server-side, the app constructs `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: {...shop-domain: "victim.myshopify.com", hmac-sha256: H...})` and calls `Registry.process(request)`.
4. `Utils::HmacValidator.validate(request)` succeeds because it only checks `HMAC(secret, B) == H`, per [7](#0-6) .
5. `Registry.process` invokes the app's handler with `WebhookMetadata.new(..., shop: "victim.myshopify.com", body: parsed(B), ...)`, per [8](#0-7) , causing the host application to process attacker-controlled data as belonging to `victim.myshopify.com`.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-23)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/webhooks/registry.rb (L188-199)
```ruby
        sig { params(request: Request).void }
        def process(request)
          raise Errors::InvalidWebhookError, "Invalid webhook HMAC." unless Utils::HmacValidator.validate(request)

          handler = @registry[request.topic]&.handler

          unless handler
            raise Errors::NoWebhookHandler, "No webhook handler found for topic: #{request.topic}."
          end

          handler.handle(data: WebhookMetadata.new(topic: request.topic, shop: request.shop,
            body: request.parsed_body, api_version: request.api_version, webhook_id: request.webhook_id))
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

**File:** lib/shopify_api/auth/jwt_payload.rb (L33-45)
```ruby
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
```
