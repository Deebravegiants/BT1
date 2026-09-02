Confirmed: `Registry.process` at `lib/shopify_api/webhooks/registry.rb:189-199` validates only `Utils::HmacValidator.validate(request)`, which HMACs `request.to_signable_string` = `@raw_body` only (`lib/shopify_api/webhooks/request.rb:36-38`). The `shop` (`shop-domain` header, line 21-23) and `topic` (line 16-18) are read directly from unauthenticated HTTP headers and passed straight into `WebhookMetadata.new(topic: request.topic, shop: request.shop, ...)` (`registry.rb:198-199`) without being covered by the signature.

### Title
Webhook `shop`/`topic` identity fields are not covered by the HMAC signature, enabling cross-tenant webhook spoofing - (File: lib/shopify_api/webhooks/request.rb, lib/shopify_api/webhooks/registry.rb)

### Summary
`ShopifyAPI::Webhooks::Registry.process` authenticates an inbound webhook solely by validating the HMAC over the raw request body via `Utils::HmacValidator.validate` [1](#0-0) . The `Request#to_signable_string` used for that HMAC computation returns only `@raw_body` [2](#0-1) , while `shop` and `topic`, which come from the `shopify-shop-domain`/`x-shopify-shop-domain` and `shopify-topic`/`x-shopify-topic` HTTP headers respectively, are read unauthenticated and forwarded to the handler [3](#0-2) .

### Finding Description
The identity binding that should hold is: `hmac_signature == HMAC(secret, shop || topic || body)`, i.e. the tenant (`shop`) and event type (`topic`) that a handler acts on should be cryptographically bound to the signature that authenticates the message. Instead, the actual binding implemented is `hmac_signature == HMAC(secret, body)` only [2](#0-1) , while `shop` and `topic` are taken from plain, unsigned headers [3](#0-2) .

Because a single app uses the same `api_secret_key` for HMAC signing across all shops that install it, any merchant/shop that legitimately receives a webhook (a valid `body` + `hmac` pair signed with the app's shared secret) can replay that exact body+hmac to the app's webhook endpoint while substituting a different `shop-domain` header (any other shop that also installed the app) and/or a different `topic` header for another registered topic that expects a compatible body shape. `Registry.process` will validate the HMAC successfully (it only checks the body) and dispatch to the handler with attacker-chosen `shop`/`topic` metadata [4](#0-3) , causing the app to attribute/act on the event as belonging to a different tenant (`WebhookMetadata.shop`) than the one that actually produced the signed bytes.

### Impact Explanation
This breaks the binding between the authenticated bytes (body signed by the shared app secret) and the tenant identity (`shop`) the host application will use to look up sessions, update records, or trigger tenant-scoped side effects for a webhook handler. This is a cross-tenant data confusion vector: an unprivileged party in control of one shop's webhook traffic can cause the app to process events attributed to a different shop, without ever needing that shop's access token, session, or the app's `client_secret`. This satisfies the "cross-tenant access" criterion.

### Likelihood Explanation
Exploitation requires only capturing/replaying a body+hmac pair from any shop using the same app (trivial for the attacker's own installed shop) and re-sending it to the app's public webhook endpoint with modified `shop-domain`/`topic` headers — no secrets, tokens, or privileged access are required. The main constraint is that the replayed body must make semantic sense for the spoofed `topic`/`shop` in the host application's handler logic, but many webhook bodies (e.g. generic app/uninstall, product, or order payloads) are shop-agnostic in structure.

### Recommendation
Include `shop` and `topic` (and ideally `webhook_id`) as part of the signed material verified against the HMAC, or otherwise cryptographically bind them (e.g., require the host app to re-verify `shop` against a known, previously-registered set of shops before trusting `WebhookMetadata.shop`). Alternatively, document explicitly that `shop`/`topic` are not authenticated by `HmacValidator.validate` and that host applications must independently verify tenant identity before acting on `WebhookMetadata`.

### Proof of Concept
1. App is installed on `shop-a.myshopify.com` and `shop-b.myshopify.com`, both webhooks signed with the same `api_secret_key`.
2. Attacker (merchant of `shop-a`) triggers a legitimate webhook event on their own store, capturing the raw request body `B` and the valid `X-Shopify-Hmac-Sha256: H` header Shopify sent to the app.
3. Attacker resends an HTTP POST to the app's webhook endpoint with the same body `B` and header `H`, but sets `X-Shopify-Shop-Domain: shop-b.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` accepts the request (all required headers present) [5](#0-4) ; `Utils::HmacValidator.validate` succeeds because it only verifies `body` against `H` [6](#0-5) .
5. `Registry.process` dispatches to the registered handler with `WebhookMetadata.new(shop: "shop-b.myshopify.com", topic: ..., body: parsed_body)` [7](#0-6) , causing the host application's handler to process shop-a's data as if it were shop-b's webhook.

### Citations

**File:** lib/shopify_api/webhooks/registry.rb (L188-200)
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
        end
```

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

**File:** lib/shopify_api/webhooks/request.rb (L45-63)
```ruby
      sig { params(raw_body: String, headers: T::Hash[String, T.untyped]).void }
      def initialize(raw_body:, headers:)
        # normalize the headers by forcing lowercase, removing any prepended "http"s, and changing underscores to dashes
        headers = headers.to_h { |k, v| [k.to_s.downcase.sub("http_", "").gsub("_", "-"), v] }

        missing_headers = []
        ["topic", "hmac-sha256", "shop-domain"].each do |name|
          unless headers.key?("shopify-#{name}") || headers.key?("x-shopify-#{name}")
            missing_headers << "shopify-#{name} or x-shopify-#{name}"
          end
        end
        unless missing_headers.empty?
          raise Errors::InvalidWebhookError,
            "Missing one or more of the required HTTP headers to process webhooks: #{missing_headers}"
        end

        @headers = headers
        @raw_body = raw_body
      end
```

**File:** lib/shopify_api/utils/hmac_validator.rb (L12-22)
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
```
