### Title
Webhook shop-domain and topic headers are trusted for tenant routing without being covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an incoming webhook solely by validating the HMAC over the raw request body, then unconditionally trusts the unauthenticated `shop-domain` and `topic` HTTP headers to route the payload and identify the tenant. Because these header values are not part of the signed content, they can be swapped on an otherwise validly-signed request without invalidating the signature, breaking the binding between "HMAC-authenticated bytes" and "shop identity acted upon."

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only `@raw_body`: [1](#0-0) 

The `shop` and `topic` accessors read directly from HTTP headers, which are attacker-controlled and are never mixed into the signable string: [2](#0-1) 

`Registry.process` validates only the HMAC (over the body) via `Utils::HmacValidator.validate(request)`, then immediately builds a `WebhookMetadata` struct from the *headers* (`request.topic`, `request.shop`) and hands it to the app-registered handler: [3](#0-2) 

`HmacValidator.validate` computes the signature from `verifiable_query.to_signable_string` (the body only) and the app's `Context.api_secret_key`, comparing it against the `hmac-sha256` header: [4](#0-3) 

`WebhookMetadata.shop` is exactly the value handed to the host application's handler as the tenant identifier for the webhook: [5](#0-4) 

The equality that should hold is: `shop bound by HMAC == shop acted upon by the handler`. In this implementation, `shop acted upon` is read straight from the `x-shopify-shop-domain`/`shopify-shop-domain` header, which is completely outside the HMAC's scope (only `@raw_body` is signed). An unprivileged user who controls any merchant store that has webhooks configured to point at the app (e.g., their own trial/dev store, or any store where they can trigger a webhook with attacker-influenced body content) can capture a validly-signed webhook request and replay it with a different `shop-domain` header value, and the signature check still passes because the header isn't part of the signed bytes. The handler will then process the (attacker's) payload as if it came from a different shop.

### Impact Explanation
This crosses a tenant boundary: the gem allows a webhook payload that is only proven authentic for "some shop, with this raw body" to be attributed to an arbitrary target shop domain chosen by the requester, since the shop domain is not bound into the HMAC-checked bytes. Any host application that uses `WebhookMetadata#shop` (the officially provided, gem-documented field) to look up per-tenant state, session/access tokens, or to gate/scope handler logic will act on attacker-chosen shop identity backed only by an HMAC that never covered that identity. This matches the report's flagged bug class of "a field acted on but not covered by the HMAC," rated High due to cross-tenant confusion/impersonation via a credential-adjacent authentication check (the webhook HMAC is this gem's authentication mechanism for webhooks).

### Likelihood Explanation
Exploitability requires only the ability to submit an HTTP POST with attacker-controlled headers directly to the app's webhook endpoint alongside body bytes that are HMAC-signed by Shopify for *some* shop (e.g., a webhook fired from a store the attacker can install the app to, a trial store, or another tenant's leaked/observed payload). No access token, `client_secret`, or Shopify-side privilege is required — only network access to the app's public webhook endpoint and one legitimately-signed payload to replay with a modified `shop-domain` header. This is a realistic "unprivileged internet user" scenario since webhook endpoints are internet-reachable by design.

### Recommendation
Include the `shop-domain` (and ideally `topic`) header value in the HMAC-signed content, or otherwise cryptographically bind them to the payload, so that any tampering with these headers invalidates the signature. At minimum, `Request#to_signable_string` should incorporate the shop domain (mirroring how Shopify's own webhook HMAC verification is documented to only cover the raw body — the gem should independently corroborate the `shop-domain` header against a value obtained through an authenticated channel, e.g., matching it against sessions/known installed shops) before handing `WebhookMetadata` to handlers, and document that host apps must not treat `WebhookMetadata#shop` as authenticated by the HMAC without additional verification against known/installed shop records.

### Proof of Concept
1. Attacker installs (or otherwise triggers a webhook from) shop `attacker-shop.myshopify.com`, which is a valid Shopify tenant for the target app, with a webhook body `B`. Shopify signs `B` with the app's shared secret, producing `hmac-sha256 = HMAC(secret, B)`, and sends headers `x-shopify-shop-domain: attacker-shop.myshopify.com`, `x-shopify-hmac-sha256: <valid>`.
2. Attacker intercepts/replays this exact request to the app's webhook endpoint but changes only the header `x-shopify-shop-domain` to `victim-shop.myshopify.com`, leaving body `B` and the `hmac-sha256` header untouched.
3. `ShopifyAPI::Webhooks::Request.new(raw_body: B, headers: tampered_headers)` builds a `Request` whose `to_signable_string` still returns `B`: [1](#0-0) 
4. `Registry.process(request)` calls `Utils::HmacValidator.validate(request)`, which recomputes `HMAC(secret, B)` and compares it to the untouched, still-valid `hmac-sha256` header — validation **passes**: [6](#0-5) 
5. `Registry.process` builds `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` using the tampered `shop-domain` header value (`victim-shop.myshopify.com`) and dispatches it to the app's handler: [7](#0-6) 
6. The host application's handler receives `data.shop == "victim-shop.myshopify.com"` despite the payload never having been authenticated for that shop, allowing the attacker to inject/attribute webhook content to a tenant they do not control.

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

**File:** lib/shopify_api/webhooks/webhook_handler.rb (L6-12)
```ruby
    class WebhookMetadata < T::Struct
      const :topic, String
      const :shop, String
      const :body, T::Hash[String, T.untyped]
      const :api_version, String
      const :webhook_id, String
    end
```
