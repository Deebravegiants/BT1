### Title
Webhook `shop`, `topic`, and `webhook-id` fields are trusted for tenant/handler routing but are not covered by the HMAC signature - (File: lib/shopify_api/webhooks/request.rb)

### Summary
`ShopifyAPI::Webhooks::Request` computes its HMAC-verifiable payload from the raw HTTP body only, while the shop identity, topic, and webhook-id used for tenant routing and handler dispatch come from unauthenticated HTTP headers.

### Finding Description
`Request#to_signable_string` returns only `@raw_body`: ` [1](#0-0) `. `Utils::HmacValidator.validate` computes the HMAC over exactly that signable string and constant-time-compares it to the `hmac` accessor: ` [2](#0-1) `. Meanwhile, `shop`, `topic`, `api_version`, and `webhook_id` are read straight from request headers with no cryptographic binding to the body or to each other: ` [3](#0-2) `. `Registry.process` only checks `Utils::HmacValidator.validate(request)` (i.e., that *some* valid body/HMAC pair exists) and then dispatches the handler and constructs `WebhookMetadata` using the unauthenticated `request.shop`, `request.topic`, and `request.webhook_id`: ` [4](#0-3) `.

This breaks the intended identity binding `hmac(signed content) == hmac(content acted upon)`: the gem verifies the *body* bytes but acts on the *shop/topic/webhook-id* bytes, which are never part of the signed content. Because the HMAC secret (`api_secret_key`/`client_secret`) is shared across all shops that install a given app (it is not shop-specific), any merchant who legitimately installs the app on their own store can obtain a genuine `(raw_body, hmac)` pair from a real Shopify-sent webhook, then replay that exact body/HMAC to the app's webhook endpoint while substituting arbitrary `x-shopify-shop-domain`, `x-shopify-topic`, and `x-shopify-webhook-id` header values. The HMAC check still passes (it only proves the body was produced with the shared app secret, not which shop or topic it belongs to), and `Registry.process` will hand the (real, valid-looking) body to whatever handler is registered for the attacker-chosen `topic`, tagged with an attacker-chosen `shop` in `WebhookMetadata`.

### Impact Explanation
This directly enables cross-tenant confusion/impersonation: a host application that persists or acts on webhook data keyed by `WebhookMetadata#shop` (as the gem's own documented `WebhookMetadata` design intends, per ` [5](#0-4) `) can be made to attribute a legitimately-signed payload to a shop that never sent it — e.g., marking a victim shop's subscription/state changed, or feeding attacker-controlled (but validly-HMAC'd) data into a handler for a topic never actually delivered by Shopify for that body. This matches the "Critical – cross-tenant access" impact category, since the tenant boundary (`shop`) that the gem exposes to host-app handlers is not authenticated.

### Likelihood Explanation
The prerequisite is only that the attacker be an ordinary merchant capable of installing the target app on their own store (no privileged credentials, no access token, no `api_secret_key` needed) and capable of sending arbitrary HTTP headers to the app's public webhook endpoint — both are within reach of an unprivileged internet user. The header/body decoupling is deterministic and requires no timing or race conditions.

### Recommendation
Bind the tenant/topic identity into the verified signature material, or otherwise cryptographically link headers to the body before they are trusted for routing/tenant-attribution — e.g., include `shop`, `topic`, and `webhook_id` in `to_signable_string`, or have `Registry.process` cross-check them against an out-of-band trusted source before constructing `WebhookMetadata`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and lets Shopify deliver a real webhook (e.g., `app/uninstalled`) to the app's endpoint. They capture the raw body `B` and the valid `x-shopify-hmac-sha256` header `H` (computed by Shopify with the app's shared secret).
2. Attacker resends an HTTP request to the same endpoint with body `B`, header `x-shopify-hmac-sha256: H` (unchanged, still valid per ` [1](#0-0) `), but sets `x-shopify-shop-domain: victim.myshopify.com` and `x-shopify-topic: orders/create` (or any topic the host app has registered a sensitive handler for).
3. `HmacValidator.validate` succeeds because only `B` and `H` are checked (` [6](#0-5) `); `Registry.process` dispatches to the `orders/create` handler with `WebhookMetadata#shop == "victim.myshopify.com"` (` [4](#0-3) `), even though Shopify never sent this topic/shop combination.

### Citations

**File:** lib/shopify_api/webhooks/request.rb (L15-33)
```ruby
      sig { returns(String) }
      def topic
        T.cast(shopify_header("topic"), String)
      end

      sig { returns(String) }
      def shop
        T.cast(shopify_header("shop-domain"), String)
      end

      sig { returns(String) }
      def api_version
        T.cast(shopify_header("api-version"), String)
      end

      sig { returns(String) }
      def webhook_id
        T.cast(shopify_header("webhook-id"), String)
      end
```

**File:** lib/shopify_api/webhooks/request.rb (L35-38)
```ruby
      sig { override.returns(String) }
      def to_signable_string
        @raw_body
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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
        sig { params(verifiable_query: VerifiableQuery, secret: String).returns(T::Boolean) }
        def validate_signature(verifiable_query, secret)
          received_signature = verifiable_query.hmac
          computed_signature = compute_signature(verifiable_query.to_signable_string, secret)
          OpenSSL.secure_compare(computed_signature, T.must(received_signature))
        end
```

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
