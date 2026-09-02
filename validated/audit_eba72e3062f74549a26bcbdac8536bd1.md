### Title
Webhook `shop` (and `topic`/`webhook_id`) header is not covered by the HMAC signature, allowing cross-tenant webhook spoofing - ([File: lib/shopify_api/webhooks/request.rb])

### Summary
`ShopifyAPI::Webhooks::Registry.process` is documented to "verify the request did indeed come from Shopify" before invoking the app's handler, but the HMAC it validates only covers the raw request body. The `shop`, `topic`, `webhook_id`, and `api_version` values — all taken from unauthenticated HTTP headers — are handed to the handler unverified. An attacker who can obtain any single valid `(body, hmac)` pair (trivially, by installing the target app on their own free Shopify dev store and capturing one of its own legitimately-signed webhooks) can replay that body/HMAC to the app's webhook endpoint while substituting an arbitrary `shop-domain` header, causing the app to process attacker-supplied data as if it originated from a victim shop.

### Finding Description
`ShopifyAPI::Webhooks::Request#to_signable_string` returns only the raw body: [1](#0-0) 

The `shop`, `topic`, `webhook_id`, and `api_version` accessors read directly from attacker-controllable HTTP headers and are never included in the signed content: [2](#0-1) 

`Utils::HmacValidator.validate` computes/compares the HMAC purely over `to_signable_string`, i.e., only the body bytes: [3](#0-2) 

`Registry.process` uses that HMAC check as its sole authenticity gate, then immediately trusts `request.shop`, `request.topic`, and `request.webhook_id` to build the `WebhookMetadata` passed to the app's handler: [4](#0-3) 

The gem's own documentation asserts a stronger guarantee than what is actually enforced — that `process` "will verify the request did indeed come from Shopify": [5](#0-4) 

In reality, only the body's integrity/authenticity is proven. The identity binding broken is: `shop` (the tenant the handler believes the webhook is scoped to) ≠ `shop` (the tenant whose secret actually produced the HMAC) — because `shop` is never an input to the signature at all.

### Impact Explanation
Any consumer of this gem that follows the documented `Registry.process` pattern and trusts `WebhookMetadata#shop` (as the docs' own example handler does: `shop_domain: data.shop`) can be made to process webhook bodies under an arbitrary, attacker-chosen shop identity. Since an attacker only needs one legitimately-signed body from *any* shop (including a free store they install the app on themselves), they can forge the `shop-domain` header to point at any other merchant using the app, causing cross-tenant data confusion in the host application — e.g., an app that syncs order/product data keyed by `data.shop` could write or act upon a victim shop's records using attacker-supplied content. This matches the "Critical – cross-tenant access" impact category.

### Likelihood Explanation
Likelihood is high: no privileged credentials, access tokens, or `api_secret_key` are needed. The only prerequisite is the ability to obtain one valid `(body, hmac)` pair, which is achievable by any unprivileged internet user by installing the target app on a free Shopify development/partner store and capturing its own genuine webhook delivery, then replaying it with a modified `shop-domain` header against the app's public webhook endpoint.

### Recommendation
Include `shop`, `topic`, and `webhook_id` in the HMAC-signed material (or otherwise cryptographically bind them to the payload), and/or require host applications to independently verify that `request.shop` corresponds to a shop with an active, known installation before trusting `WebhookMetadata#shop`. At minimum, correct the documentation in `docs/usage/webhooks.md` to clarify that `process` only authenticates the request body, not the shop/topic headers, so host applications don't over-trust `data.shop`.

### Proof of Concept
1. Attacker installs the target Shopify app on their own store `attacker.myshopify.com` and registers a webhook (e.g., `orders/create`).
2. Shopify delivers a legitimately HMAC-signed webhook to the app's endpoint: headers include `x-shopify-shop-domain: attacker.myshopify.com`, `x-shopify-hmac-sha256: <valid-hmac-of-body>`, plus the raw body.
3. Attacker intercepts/replays this exact `(raw_body, hmac)` to the same app endpoint but rewrites the header to `x-shopify-shop-domain: victim.myshopify.com`.
4. `ShopifyAPI::Webhooks::Request.new` parses this into a request object; `Utils::HmacValidator.validate(request)` succeeds because it only checks `raw_body` against the HMAC (`lib/shopify_api/webhooks/request.rb:36-38`, `lib/shopify_api/utils/hmac_validator.rb:26-31`).
5. `Registry.process` (`lib/shopify_api/webhooks/registry.rb:188-199`) invokes the app's handler with `shop: "victim.myshopify.com"` and the attacker-controlled body, even though nothing about the request actually proves it originated from or concerns `victim.myshopify.com`.

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

**File:** lib/shopify_api/utils/hmac_validator.rb (L26-31)
```ruby
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

**File:** docs/usage/webhooks.md (L123-125)
```markdown
## Process a Webhook

To process an http webhook, you need to listen on the route(s) you provided during the Webhook registration process, then when the route is hit construct a `ShopifyAPI::Webhooks::Request` and call `ShopifyAPI::Webhooks::Registry.process`. This will verify the request did indeed come from Shopify and then call the specified handler for that webhook. An example in Rails is shown below:
```
