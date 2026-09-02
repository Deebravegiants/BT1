### Title
Webhook `shop-domain` header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Request#to_signable_string` only returns the raw request body, so the HMAC that `ShopifyAPI::Webhooks::Registry.process` validates covers the payload bytes but not the `shopify-shop-domain` header that the library later hands to the app's webhook handler as the authoritative tenant identifier.

### Finding Description
`Request#to_signable_string` is defined as: [1](#0-0) 

only the `@raw_body` is signed. The `shop` accessor, however, comes from an unauthenticated header: [2](#0-1) 

`Registry.process` validates the HMAC and, on success, unconditionally trusts `request.shop` to build the metadata that is dispatched to the host app's handler: [3](#0-2) 

The HMAC secret (`Context.api_secret_key`) is shared across every shop that installs the app — it is not per-tenant. Any merchant who installs the app receives genuine webhooks (real body + valid HMAC) addressed to their own shop. Because the `shop-domain` header is outside the signed content, that same captured `(body, hmac)` pair can be POSTed to the app's webhook endpoint again with the `x-shopify-shop-domain` (or `shopify-shop-domain`) header rewritten to name a *different* victim shop. `HmacValidator.validate` will still pass because it only recomputes the signature over the body: [4](#0-3) 

and `Registry.process` performs no additional binding check between the authenticated bytes and the `shop` field before invoking the handler with `request.shop`.

This is exactly the "field acted on but not covered by the HMAC" identity-binding gap: the equality that should hold is `shop_bound_by_hmac == shop_used_by_handler`, but the gem only guarantees `hmac_computed(body) == hmac_received`, leaving `shop` entirely attacker-controlled.

### Impact Explanation
Any application that relies on `WebhookMetadata#shop` (as the docs and registry code direct) to select which tenant's data to update will process an attacker-supplied event under an arbitrary victim shop identifier, despite the underlying payload only ever having been legitimately generated for the attacker's own shop. This is a cross-tenant confusion primitive delivered entirely from an unprivileged internet-facing endpoint (the app's public webhook URL), matching the "cross-tenant access" impact category.

### Likelihood Explanation
Exploitation requires only: (1) installing the target app on an attacker-controlled shop to receive at least one legitimate webhook (trivial for any public/embedded Shopify app), and (2) POSTing the captured body/HMAC to the app's public webhook endpoint with a forged shop header — both actions achievable by any unprivileged internet user with no access to `client_secret`, tokens, or the target shop's credentials.

### Recommendation
Include the shop domain (and ideally topic/webhook-id/api-version) in the signable string used for webhook HMAC verification, or otherwise cryptographically bind the `shop` header to the payload before it is trusted by `Registry.process`/`WebhookMetadata`. At minimum, document that host applications must independently verify `request.shop` against a known, previously-registered shop for that specific webhook subscription rather than trusting the header as authenticated.

### Proof of Concept
1. Attacker installs the target Shopify app on `attacker-shop.myshopify.com` and triggers/receives a legitimate webhook, capturing `raw_body` and the valid `x-shopify-hmac-sha256` header (both are computed using the app's single, shared `api_secret_key`).
2. Attacker replays the exact same `raw_body` and `x-shopify-hmac-sha256` to the app's public webhook endpoint, but sets `x-shopify-shop-domain: victim-shop.myshopify.com`.
3. `ShopifyAPI::Webhooks::Request.new` accepts the forged headers (only checks presence, not shop authenticity): [5](#0-4) 
4. `Registry.process` calls `Utils::HmacValidator.validate(request)`, which succeeds because it only checks `raw_body` against the HMAC: [6](#0-5) 
5. The handler is invoked with `shop: request.shop` set to `victim-shop.myshopify.com`, even though the payload was never generated for that shop, causing the host application to attribute/act on the event as if it originated from the victim tenant.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L20-23)
```ruby
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
